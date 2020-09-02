"""

    Test Convex Contracts for Starfish

"""
import re
import pytest
import secrets

from convex_api.account import Account
from convex_api.convex_api import ConvexAPI
from convex_api.exceptions import ConvexAPIError


def test_contract_did_registry(convex_url, test_account):
    did_registry_contract = """
(def starfish-did-registry
    (deploy
        '(do
            (def registry {})
            (defn resolve? [did] (boolean (get registry did)))
            (defn resolve [did]
                (if (resolve? did) ((get registry did) :ddo))
            )
            (defn owner [did]
                (if (resolve? did) ((get registry did) :owner))
            )
            (defn owner? [did] (= (owner did) *caller*))
            (defn register [did ddo]
                (if (resolve? did) (assert (owner? did)))
                (let [ddo-record {:owner *caller* :ddo ddo}]
                    (def registry (assoc registry did ddo-record))
                    did
                )
            )
            (defn unregister [did]
                (if (resolve? did) (do
                    (assert (owner? did))
                    (def registry (dissoc registry did))
                    did
                    )
                )
            )
            (export resolve resolve? register unregister owner owner?)
        )
    )
)
"""

    deploy_single_contract_did_registry = """
# single contract per did, deployed contract is the didid
(def starfish-did-registry
    (deploy
        '(do
            (def store-owner *caller*)
            (def store-ddo nil)
            (defn resolve [] store-ddo)
            (defn register[x]
                (assert (owner?))
                (def store-ddo x)
            )
            (defn owner? [] (= store-owner *caller*))
            (defn owner [] store-owner)
            (export resolve register owner? owner)
        )
    )
)
"""
    convex = ConvexAPI(convex_url)
    amount = 10000000
    request_amount = convex.request_funds(amount, test_account)

    other_account = Account.create_new()
    request_amount = convex.request_funds(amount, other_account)

    result = convex.send(did_registry_contract, test_account)
    assert(result['value'])
    contract_address = re.sub(r'#addr ', '', result['value'])
    print(contract_address)

    did = secrets.token_hex(32)
    ddo = 'test - ddo'

    # call register

    command = f'(call {contract_address} (register "{did}" "{ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to ddo

    command = f'(call {contract_address} (resolve "{did}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call resolve did to ddo on other account

    command = f'(call {contract_address} (resolve "{did}"))'
    result = convex.send(command, other_account)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call owner? on owner account
    command = f'(call {contract_address} (owner? "{did}"))'
    result = convex.send(command, test_account)
    assert(result['value'])

    # call owner? on owner other_account
    command = f'(call {contract_address} (owner? "{did}"))'
    result = convex.send(command, other_account)
    assert(not result['value'])

    # call resolve unknown
    bad_did = secrets.token_hex(32)
    command = f'(call {contract_address} (resolve "{bad_did}"))'
    result = convex.send(command, test_account)
    assert(result['value'] == '')


    new_ddo = 'new - ddo'
    # call register - update

    command = f'(call {contract_address} (register "{did}" "{new_ddo}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)


    # call register - update from other account

    with pytest.raises(ConvexAPIError, match='ASSERT'):
        command = f'(call {contract_address} (register "{did}" "{ddo}"))'
        result = convex.send(command, other_account)


    # call resolve did to new_ddo

    command = f'(call {contract_address} (resolve "{did}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == new_ddo)


    # call unregister fail - from other account

    with pytest.raises(ConvexAPIError, match='ASSERT'):
        command = f'(call {contract_address} (unregister "{did}"))'
        result = convex.send(command, other_account)


    # call unregister

    command = f'(call {contract_address} (unregister "{did}"))'
    result = convex.send(command, test_account)
    assert(result['value'])
    assert(result['value'] == did)

    # call resolve did to empty

    command = f'(call {contract_address} (resolve "{did}"))'
    result = convex.send(command, test_account)
    assert(result['value'] == '')


    # call unregister - unknown did

    command = f'(call {contract_address} (unregister "{bad_did}"))'
    result = convex.send(command, test_account)
    assert(result['value'] == '')


