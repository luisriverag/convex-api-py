"""

    Account class for convex api


"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from eth_utils import (
    remove_0x_prefix,
    to_bytes,
    to_hex
)

from mnemonic import Mnemonic

from convex_api.utils import (
    to_address,
    to_public_key_checksum
)


class Account:
    """

        The Convex account class, contains the public/private keys and possibly an address.

        You can create a new account object, it will only have it's public/private keys but does not have a valid account address.
        To obtain a new account address, you need to call the :py:meth:`.ConvexAPI.create_account` with the new account object.

        This is so that you can use the same public/private keys for multiple convex accounts.

        Once you have your new account you need to save the public/private keys using the `export..` methods and also you
        need to save the account address.

        To re-use the account again, you can import the keys and set the account address using one of the `import..` methods.

    """
    def __init__(self, private_key, address=None):
        """
        Create a new account with a private key as a Ed25519PrivateKey

        :param Ed25519PrivateKey private_key: The public/private key as an Ed25519PrivateKey object
        :param int address: address of the account

        """
        self._private_key = private_key
        self._public_key = private_key.public_key()
        self._address = None
        if address is not None:
            self._address = to_address(address)

    def sign(self, hash_text):
        """
        Sign a hash text using the private key.

        :param str hash_text: Hex string of the hash to sign

        :returns: Hex string of the signed text

        """
        hash_data = to_bytes(hexstr=hash_text)
        signed_hash_bytes = self._private_key.sign(hash_data)
        return to_hex(signed_hash_bytes)

    def export_to_text(self, password):
        """
        Export the private key to an encrypted PEM string.

        :param str password: Password to encrypt the private key value

        :returns: The private key as a PEM formated encrypted string

        """
        if isinstance(password, str):
            password = password.encode()
        private_data = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password)
        )
        return private_data.decode()

    @property
    def export_to_mnemonic(self):
        mnemonic = Mnemonic('english')
        return mnemonic.to_mnemonic(self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        ))

    def export_to_file(self, filename, password):
        """
        Export the private key to a file. This uses `export_to_text` to export as a string.
        Then saves this in a file.

        :param str filename: Filename to create with the PEM string
        :param str password: Password to use to encypt the private key

        """
        with open(filename, 'w') as fp:
            fp.write(self.export_to_text(password))

    def __str__(self):
        return f'Account {self.address}'

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = to_address(value)

    @property
    def public_key_bytes(self):
        """
        Return the public key address of the account in the byte format

        :returns: str Address in bytes

        """
        public_key_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return public_key_bytes

    @property
    def public_key(self):
        """
        Return the public key of the account in the format '0x....'

        :returns: str public_key with leading '0x'

        """
        return to_hex(self.public_key_bytes)

    @property
    def public_key_api(self):
        """
        Return the public key of the account without the leading '0x'

        :returns: str public_key without the leading '0x'

        """
        return remove_0x_prefix(self.public_key)

    @property
    def public_key_checksum(self):
        """
        Return the public key of the account with checksum upper/lower case characters

        :returns: str public_key in checksum format

        """

        return to_public_key_checksum(self.public_key)

    @staticmethod
    def create():
        """
        Create a new account with a random key and address

        :returns: New Account object

        """
        return Account(Ed25519PrivateKey.generate())

    @staticmethod
    def import_from_bytes(value, address=None):
        """
        Import an account from a private key in bytes.

        :param int address: address of the account

        :returns: Account object with the private/public key

        """
        return Account(Ed25519PrivateKey.from_private_bytes(value), address=address)

    @staticmethod
    def import_from_text(text, password, address=None):
        """
        Import an accout from an encrypted PEM string.

        :param str text: PAM text string with the encrypted key text
        :param str password: password to decrypt the private key
        :param int address: address of the account

        :returns: Account object with the public/private key

        """
        if isinstance(password, str):
            password = password.encode()
        if isinstance(text, str):
            text = text.encode()

        private_key = serialization.load_pem_private_key(text, password, backend=default_backend())
        if private_key:
            return Account(private_key, address=address)

    @staticmethod
    def import_from_mnemonic(words, address=None):
        mnemonic = Mnemonic('english')
        value = mnemonic.to_entropy(words)
        return Account(Ed25519PrivateKey.from_private_bytes(value), address=address)

    @staticmethod
    def import_from_file(filename, password, address=None):
        """
        Load the encrypted private key from file. The file is saved in PEM format encrypted with a password

        :param str filename: Filename to read
        :param str password: password to decrypt the private key
        :param int address: address of the account

        :returns: Account with the private/public key

        """
        with open(filename, 'r') as fp:
            return Account.import_from_text(fp.read(), password, address=address)
