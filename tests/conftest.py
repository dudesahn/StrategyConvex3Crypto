import pytest
from brownie import config, Wei, Contract

# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass

# Define relevant tokens and contracts in this section

@pytest.fixture
def token():
    # this should be the address of the ERC-20 used by the strategy/vault. In this case, Curve's Iron Bank Pool token
    token_address = "0x5282a4eF67D9C33135340fB3289cc1711c13638C"
    yield Contract(token_address)


@pytest.fixture
def crv():
    yield Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")

@pytest.fixture
def cvx():
    yield Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")

@pytest.fixture
def dai():
    yield Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture
def voter():
    # this is yearn's veCRV voter, where all gauge tokens are held (for v2 curve gauges that are tokenized)
    yield Contract("0xF147b8125d2ef93FB6965Db97D6746952a133934")


@pytest.fixture
def gaugeIB():
    # this is the gauge contract for the Iron Bank Curve Pool, in Curve v2 these are tokenized.
    yield Contract("0xF5194c3325202F456c95c1Cf0cA36f8475C1949F")

# Define any accounts in this section
@pytest.fixture
def gov(accounts):
    # yearn multis... I mean YFI governance. I swear!
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)

@pytest.fixture
def dudesahn(accounts):
    yield accounts.at("0x8Ef63b525fceF7f8662D98F77f5C9A86ae7dFE09", force=True)

@pytest.fixture
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)

@pytest.fixture
def keeper(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]

@pytest.fixture
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)

@pytest.fixture
def whale(accounts):
    # Totally in it for the tech (largest EOA holder of ib-3crv, ~600k worth)
    whale = accounts.at('0xE594173Aaa1493665EC6A19a0D170C76EEa1124a', force=True)
    yield whale

# this is the live strategy for ib3crv
@pytest.fixture
def curveVoterProxyStrategy():
    yield Contract("0x5148C3124B42e73CA4e15EEd1B304DB59E0F2AF7")

@pytest.fixture
def strategy(strategist, keeper, vault, StrategyConvexCurveLP, gov, curveVoterProxyStrategy, guardian):
	# parameters for this are: strategy, vault, max deposit, minTimePerInvest, slippage protection (10000 = 100% slippage allowed), 
	# staking pool (4 for alUSD-3Crv on masterchef), asset number (0 alUSD, 1 DAI, 2 USDC, 3 USDT)
    strategy = guardian.deploy(StrategyConvexCurveLP, vault)
    strategy.setKeeper(keeper)
    # lower the debtRatio of genlender to make room for our new strategy
    vault.updateStrategyDebtRatio(curveVoterProxyStrategy, 5000, {"from": gov})
    vault.setManagementFee(0, {"from": gov})
    curveVoterProxyStrategy.harvest({"from": gov})
    vault.addStrategy(strategy, 1_200, 0, 0, 1000, {"from": gov})
    yield strategy

@pytest.fixture
def vault(pm):
    Vault = pm(config["dependencies"][0]).Vault
    vault = Vault.at('0x27b7b1ad7288079A66d12350c828D3C00A6F07d7')
    yield vault
