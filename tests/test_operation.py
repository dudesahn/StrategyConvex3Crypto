import brownie
from brownie import Contract
from brownie import config


def test_operation(token, old_vault, old_strategy, strategist, whale, gaugeIB, strategyProxy, chain, voter, rando):
    # Deposit to the old_vault and harvest
    amount = 100 * (10 ** 18)
    token.transfer(rando, amount, {"from": whale})
    startingRando = token.balanceOf(rando)
    token.approve(old_vault.address, amount, {"from": rando})
    old_vault.deposit(amount, {"from": rando})
    assert token.balanceOf(old_vault) == amount

    # harvest, store asset amount
    old_strategy.harvest({"from": strategist})
    # tx.call_trace(True)
    old_assets_dai = old_vault.totalAssets()
    old_proxy_balanceOf_gauge = strategyProxy.balanceOf(gaugeIB)
    old_gauge_balanceOf_voter = gaugeIB.balanceOf(voter)
    old_strategy_balance = token.balanceOf(old_strategy)
    old_estimated_total_assets = old_strategy.estimatedTotalAssets()
    old_old_vault_balance = token.balanceOf(old_vault)
    assert strategyProxy.balanceOf(gaugeIB) == amount
    assert old_assets_dai == amount
    assert old_assets_dai == strategyProxy.balanceOf(gaugeIB)

    # simulate a month of earnings
    chain.sleep(2592000)
    chain.mine(1)

    # harvest after a month, store new asset amount
    tx = old_strategy.harvest({"from": strategist})
    tx.call_trace(True)
    new_assets_dai = old_vault.totalAssets()
    new_proxy_balanceOf_gauge = strategyProxy.balanceOf(gaugeIB)
    new_gauge_balanceOf_voter = gaugeIB.balanceOf(voter)
    new_strategy_balance = token.balanceOf(old_strategy)
    new_estimated_total_assets = old_strategy.estimatedTotalAssets()
    new_old_vault_balance = token.balanceOf(old_vault)
    assert old_assets_dai == strategyProxy.balanceOf(gaugeIB)

    # Check for any assets only in the old_vault, not in the strategy
    print("\nOld old_vault Holdings: ", old_old_vault_balance)
    print("\nNew old_vault Holdings: ", new_old_vault_balance)

    # Check total assets in the strategy
    print("\nOld Strategy totalAssets: ", old_estimated_total_assets)
    print("\nNew Strategy totalAssets: ", new_estimated_total_assets)

    # Check total assets in the old_vault + strategy
    print("\nOld old_vault totalAssets: ", old_assets_dai)
    print("\nNew old_vault totalAssets: ", new_assets_dai)

    # Want token should never be in the strategy
    print("\nOld Strategy balanceOf: ", old_strategy_balance)
    print("\nNew Strategy balanceOf: ", new_strategy_balance)

    # These two calls should return the same value, and should update after every harvest call
    print("\nOld Proxy balanceOf gauge: ", old_proxy_balanceOf_gauge)
    print("\nNew Proxy balanceOf gauge: ", new_proxy_balanceOf_gauge)
    print("\nOld gauge balanceOf voter: ", old_gauge_balanceOf_voter)
    print("\nNew gauge balanceOf voter: ", new_gauge_balanceOf_voter)

    # There are two ways to check gauge token balances. Either call from the gauge token contract gauge.balanceOf(voter), or call strategyProxy.balanceOf(gauge)

    # assert strategyProxy.balanceOf(gauge) > amount
    # assert strategyProxy.balanceOf(gauge) == new_assets_dai
    # assert gauge.balanceOf(voter) == strategyProxy.balanceOf(gauge)
    # assert strategyProxy.balanceOf(gauge) == new_assets_dai
    assert new_assets_dai > old_assets_dai

    #     genericStateOfStrat(strategy, currency, old_vault)
    #     genericStateOfold_vault(old_vault, currency)

    # Display estimated APR based on the past month
    print("\nEstimated DAI APR: ", "{:.2%}".format(((new_assets_dai - old_assets_dai) * 12) / (old_assets_dai)))

    # set optimal to USDC. new_assets_dai is now our new baseline
    old_strategy.setOptimal(1)

    # simulate a month of earnings
    chain.sleep(2592000)
    chain.mine(1)

    # harvest after a month, store new asset amount after switch to USDC
    old_strategy.harvest({"from": strategist})
    new_assets_usdc = old_vault.totalAssets()
    assert strategyProxy.balanceOf(gaugeIB) > amount
    assert new_assets_usdc > new_assets_dai

    # Display estimated APR based on the past month
    print("\nEstimated USDC APR: ", "{:.2%}".format(((new_assets_usdc - new_assets_dai) * 12) / (new_assets_dai)))

    # set optimal to USDT, new_assets_usdc is now our new baseline
    old_strategy.setOptimal(2)

    # simulate a month of earnings
    chain.sleep(2592000)
    chain.mine(1)

    # harvest after a month, store new asset amount
    old_strategy.harvest({"from": strategist})
    new_assets_usdt = old_vault.totalAssets()
    assert strategyProxy.balanceOf(gaugeIB) > amount
    assert new_assets_usdt > new_assets_usdc

    # Display estimated APR based on the past month
    print("\nEstimated USDT APR: ", "{:.2%}".format(((new_assets_usdt - new_assets_usdc) * 12) / (new_assets_usdc)))

    # wait to allow share price to reach full value (takes 6 hours as of 0.3.2)
    chain.sleep(2592000)
    chain.mine(1)

    # give rando his money back, then he sends back to whale
    old_vault.withdraw({"from": rando})    
    assert token.balanceOf(rando) >= startingRando
    endingRando = token.balanceOf(rando)
    token.transfer(whale, endingRando, {"from": rando})  