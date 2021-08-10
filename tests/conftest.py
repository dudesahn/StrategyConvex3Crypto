import pytest
from brownie import config, Wei, Contract

# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass

# Define relevant tokens and contracts in this section

@pytest.fixture
def token():
    # this should be the address of the ERC-20 used by the strategy/vault. In this case, Curve's 3crypto Pool token
    token_address = "0xc4AD29ba4B3c580e6D59105FFf484999997675Ff"
    yield Contract(token_address)

@pytest.fixture
def crv():
    yield Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")

@pytest.fixture
def cvx():
    yield Contract("0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B")

@pytest.fixture
def cvxIBDeposit():
    yield Contract("0x903C9974aAA431A765e60bC07aF45f0A1B3b61fb")

@pytest.fixture
def dai():
    yield Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")

@pytest.fixture
def rewardsContract():
    yield Contract("0x9D5C5E364D81DaB193b72db9E9BE9D8ee669B652")

@pytest.fixture
def voter():
    # this is yearn's veCRV voter, where we send all CRV to vote-lock
    yield Contract("0xF147b8125d2ef93FB6965Db97D6746952a133934")

# Define any accounts in this section
@pytest.fixture
def gov(accounts):
    # yearn multis... I mean YFI governance. I swear!
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)

@pytest.fixture
def dudesahn(accounts):
    yield accounts.at("0xBedf3Cf16ba1FcE6c3B751903Cf77E51d51E05b8", force=True)

@pytest.fixture
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)

@pytest.fixture
def new_address(accounts):
    # new account for voter and proxy tests
    yield accounts.at("0xb5DC07e23308ec663E743B1196F5a5569E4E0555", force=True)

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
    yield accounts.at("0xBedf3Cf16ba1FcE6c3B751903Cf77E51d51E05b8", force=True)

@pytest.fixture
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7", force=True)

@pytest.fixture
def whale(accounts):
    # Totally in it for the tech (largest EOA holder of ib-3crv, ~600k worth)
    whale = accounts.at('0x7a16fF8270133F063aAb6C9977183D9e72835428', force=True)
    yield whale

@pytest.fixture
def convexWhale(accounts):
    # Totally in it for the tech (largest EOA holder of CVX, ~70k worth)
    convexWhale = accounts.at('0x5F465e9fcfFc217c5849906216581a657cd60605', force=True)
    yield convexWhale

# this is the live strategy for ib3crv curve
@pytest.fixture
def curveVoterProxyStrategy():
    yield Contract("0xbA9052141cEf06FD55733D23231c37Fc856CE6F4")

# # this is the live strategy for ib3crv convex
# @pytest.fixture
# def strategy():
#     yield Contract("0x864F408B422B7d33416AC678b1a1A7E6fbcF5C8c")


@pytest.fixture
def strategy(strategist, keeper, vault, StrategyConvex3Crypto, gov, curveVoterProxyStrategy, guardian):
	# parameters for this are: strategy, vault, max deposit, minTimePerInvest, slippage protection (10000 = 100% slippage allowed), 
    strategy = guardian.deploy(StrategyConvex3Crypto, vault)
    strategy.setKeeper(keeper, {"from": gov})
    # lower the debtRatio of genlender to make room for our new strategy
    vault.updateStrategyDebtRatio(curveVoterProxyStrategy, 0, {"from": gov})
    vault.setManagementFee(0, {"from": gov})
    curveVoterProxyStrategy.harvest({"from": gov})
    vault.addStrategy(strategy, 50, 0, 2 ** 256 -1, 1000, {"from": gov})
    strategy.setStrategist('0x8Ef63b525fceF7f8662D98F77f5C9A86ae7dFE09', {"from": gov})
    strategy.harvest({"from": gov})
    yield strategy

@pytest.fixture
def vault(pm):
    Vault = pm(config["dependencies"][0]).Vault
    vault = Vault.at('0xE537B5cc158EB71037D4125BDD7538421981E6AA')
    yield vault
