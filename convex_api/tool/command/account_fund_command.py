"""

    Command Account Fund ..

"""

from convex_api import Account

from .account_utils import load_account
from .command_base import CommandBase


class AccountFundCommand(CommandBase):

    def __init__(self, sub_parser=None):
        self._command_list = []
        super().__init__('fund', sub_parser)

    def create_parser(self, sub_parser):

        parser = sub_parser.add_parser(
            self._name,
            description='Request funds for an account',
            help='Request funds for an account'
        )

        parser.add_argument(
            'name_address',
            help='account address or account name'
        )

        parser.add_argument(
            'amount',
            type=int,
            help='amount to request funds for the account'
        )

        return parser

    def execute(self, args, output):
        convex = self.load_convex(args.url)
        address = None
        name = None
        account = None
        if args.name_address:
            address = convex.resolve_account_name(args.name_address)
            name = args.name_address

        if not address:
            address = args.name_address

        if not self.is_address(address):
            output.add_error(f'{address} is not an convex account address')
            return

        import_account = load_account(args)
        if not import_account:
            output.add_error('you need to set the "--keywords" or "--password" a "--keyfile" to a valid account')
            return

        account = Account.import_from_account(import_account, address=address, name=name)

        amount = convex.request_funds(args.amount, account)
        balance = convex.get_balance(account)
        output.add_line(f'fund request for {amount} to balance: {balance} for account at {address}')
        output.set_value('amount', amount)
        output.set_value('balance', balance)
        output.set_value('address', address)
        if name:
            output.set_value('name', name)
