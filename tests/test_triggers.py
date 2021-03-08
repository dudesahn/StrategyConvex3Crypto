import brownie
from brownie import Contract
import pytest
from brownie import config


@pytest.fixture
def reserve(accounts):
    # this is the gauge contract, holds >99% of pool tokens. use this to seed our whale_triggers, as well for calling functions above as gauge
    yield accounts.at("0xF5194c3325202F456c95c1Cf0cA36f8475C1949F", force=True)         

@pytest.fixture
def whale_triggers(accounts, token ,reserve):
    # Totally in it for the tech
    # Has 5% of tokens (was in the ICO)
    a = accounts[6]
    bal = token.totalSupply() // 20
    token.transfer(a, bal, {"from":reserve})
    yield a


def test_triggers(gov, vault, strategy, token, amount, strategist, whale_triggers):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": whale_triggers})
    vault.deposit(amount, {"from": whale_triggers})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.setCrvRouter(0)
    strategy.setOptimal(0)
    strategy.harvest({"from": strategist})
    strategy.harvestTrigger(0)
    strategy.tendTrigger(0)