from typing import Any
from stellar_sdk import MuxedAccount, Server, Network, Keypair, TransactionBuilder, xdr
import requests
from decouple import config as env_var
from stellar_sdk.asset import Asset
import secrets

#Testnet Properties
horizon_server = Server("https://horizon-testnet.stellar.org/")
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE


main_key_secrets = env_var("main_key")
main_key_publickey = Keypair.from_secret(main_key_secrets).public_key

#Feebump transation acct used to pay for transaction fee
fee_key= env_var("FEEBUMP_ACCT") 
feebump_acct = Keypair.from_secret(fee_key).public_key


#Fee account, where all transaction fee are credited to
acc = env_var("TRANSACTION_FEE_CREDIT_ACCT")
credit_transaction_fee_acct = Keypair.from_secret(acc).public_key


#Fee to charge for each transaction on blockchain
transaction_fee = 10 

#Asset Key and Issuer
asset_issuer = env_var("ASSET_ISSUER")
ASSET_ISSUER = Keypair.from_secret(asset_issuer).public_key


#Asset code
asset_code = env_var("ASSET_CODE")

#Distributor Account
distributor = env_var("DISTRIBUTOR_ACCT")
DISTRIBUTOR_ACCT = Keypair.from_secret(distributor).public_key

def generate_UID() -> str:
    memo_uid = secrets.randbits(30) 
    return "255" + str(memo_uid)






def get_transaction_history_for_muxed_acct(user_muxed_acct :str) -> "Response":
    accts = MuxedAccount.from_account(user_muxed_acct)
    base_acct = accts.account_id
    memo = accts.account_muxed_id
    print(memo, base_acct)
    tx = horizon_server.operations().for_account(base_acct).call()
    all_tx = tx['_embedded']['records']
    mux_tx = [i for i in all_tx if i['type'] == 'payment' and "source_account_muxed" in i and i['source_account_muxed'] == user_muxed_acct]
    return mux_tx
def create_muxed_keypair(account_muxed_id :str, public_key=DISTRIBUTOR_ACCT) -> Any:
    """
    function to create mutiplex account for each users
    :params public_key - The base public key
    :params account_muxed_id - unique identifier for user
    """
    mux_acct = MuxedAccount(
        account_id=public_key,
        account_muxed_id=int(account_muxed_id)
    )
    items = {}
    items['muxed_acct'] = mux_acct.account_muxed
    items['memo'] = mux_acct.account_muxed_id
    
    return items

# print(create_muxed_keypair(123456))

def create_asset(asset_name : str, asset_issuer :str) -> dict:
    """
    This Create an Asset with the specified asset name and the asset total_supply
    :params: asset_name - The name of the token to create on blockchain
    :params: asset_issuer -Public key of the issuer 
    """
    asset = Asset(asset_name, asset_issuer)
    return asset


def create_trustline(secret_key :str, asset_code :str, asset_issuer :str) -> str:
    """
    This is used to create TrustLine to an asset
    :params: secret_key - The secret key of the account that wants to add trustline
    :params: asset_code - the Asset Code of the asset you want to trust
    :params: asset_issuer - The asset issuer of the asset you want to trust
    """
    key_pair = Keypair.from_secret(secret_key)
    distributor_account = horizon_server.load_account(key_pair.public_key)

    # get latest transaction fee for ledger
    base_fee = horizon_server.fetch_base_fee()

#Build transaction
    trust_transaction = (
        TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=network_passphrase,
            base_fee=base_fee,
        )
        .append_change_trust_op(
            asset_code=asset_code, asset_issuer= asset_issuer
        )
        .build()
    )

    trust_transaction.sign(secret_key)
    resp = horizon_server.submit_transaction(trust_transaction)
    return resp

def generate_key_pairs() -> Any:
    """
    This will Generated a Stellar KeyPair, they are not created Yet
    """
    keys = Keypair.random()
    return keys


def fund_with_friendBot(public_key :str):
    """
    This will fund any testnet account send to the function with testnet Lumen(XLM)
    :params: public_key - The public key to send lumen to
    """

    url = "https://friendbot.stellar.org"
    response = requests.get(url, params={"addr":public_key})
    return response

def send_internal_payments(sender_mux_acct :str, receiever_mux_acct :str, amt :str) -> Any:
    """
    This function send  payment bwt two qudiroo users to the blockchain
    """
    sender_load = MuxedAccount.from_account(sender_mux_acct)
    base_fees = horizon_server.fetch_base_fee()
    rounded_amt = round(float(amt), 6)
    
    source_acct = horizon_server.load_account(sender_load)
    print(source_acct)
    transaction_BUILD = TransactionBuilder(
        source_account=source_acct,
        network_passphrase=network_passphrase,
        base_fee=base_fees,
    ).append_payment_op(destination=receiever_mux_acct, amount=str(rounded_amt), asset_code=asset_code, asset_issuer=ASSET_ISSUER
    ).append_payment_op(destination=credit_transaction_fee_acct, amount=str(transaction_fee), asset_issuer=ASSET_ISSUER, asset_code=asset_code
    ).build()
    transaction_BUILD.sign(distributor)
    resp = horizon_server.submit_transaction(transaction_BUILD)
    return resp


def send_external_payments(sender_mux_acct :str, receiver_public_key :str, amt :str) -> xdr:
    """
    This Function Transfer token from one account to another on stellar Blockchain, fee for this transaction is paid by the feebump acct
    :params: sender_mux_acct - the sender muxed_acct
    :params: receiver_public_key - the recipient to receive the payment
    :params: amt - amount to transfer
    """
    sender_load = MuxedAccount.from_account(sender_mux_acct)

    source_acct = horizon_server.load_account(sender_load)
    rounded_amt = round(float(amt), 6)
    base_fee = horizon_server.fetch_base_fee()
    payments = TransactionBuilder(
        source_account=source_acct,
        network_passphrase=network_passphrase,
        base_fee=base_fee
        ).append_payment_op(
            destination=receiver_public_key,
            amount=str(rounded_amt),
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        ).append_payment_op(
            destination=credit_transaction_fee_acct,
            amount=str(transaction_fee),
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        ).build()
    payments.sign(distributor)
    resp = horizon_server.submit_transaction(payments)
    return resp


def quidroo_to_user_payment(receiver_acct :str, amt :str) -> xdr:
    """
    Using the recommended stellar way, an asset issuer needs a an issuer acct and a distributor acct
    this will transfer asset(QUT) from the asset issuer acct to the distributor acct(The muxed account will different who owns what on blockchain).
    this will send QUT token by default
    """
    # create_trustline(distributor, asset_code, ASSET_ISSUER)
    key_pairs = Keypair.from_secret(asset_issuer)
    sender_load = key_pairs.public_key

    source_acct = horizon_server.load_account(sender_load)
    base_fee = horizon_server.fetch_base_fee()
    payments = TransactionBuilder(
        source_account=source_acct,
        network_passphrase=network_passphrase,
        base_fee=base_fee
        ).append_payment_op(
            destination=receiver_acct,
            amount=amt,
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        #The below payment_op is for transaction fee, remove if you dont need it
        ).append_payment_op(
            destination=credit_transaction_fee_acct,
            amount=str(transaction_fee),
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        ).build()
    payments.sign(asset_issuer)
    resp = horizon_server.submit_transaction(payments)
    return resp



def token_burn(user_muxed_acct :str, amount :str) -> xdr:
    """
    user withdraw token to their bank bank, this will take token out of the total supply
    """
    sender_load = MuxedAccount.from_account(user_muxed_acct)

    source_acct = horizon_server.load_account(sender_load)

    base_fee = horizon_server.fetch_base_fee()
    payments = TransactionBuilder(
        source_account=source_acct,
        network_passphrase=network_passphrase,
        base_fee=base_fee
        ).append_payment_op(
            destination=ASSET_ISSUER,
            amount=str(round(int(amount), 7)),
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        #The below payment_op is for transaction fee, remove if you dont need it
        ).append_payment_op(
            destination=credit_transaction_fee_acct,
            amount=str(transaction_fee),
            asset_code=asset_code,
            asset_issuer=ASSET_ISSUER,
        ).build()
    payments.sign(distributor)
    resp = horizon_server.submit_transaction(payments)
    return resp