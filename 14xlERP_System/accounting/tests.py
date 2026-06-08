from django.test import TestCase
from django.contrib.auth.models import User
from .models import ChartOfAccounts, Journal, BankAccount


class ChartOfAccountsTestCase(TestCase):
    def setUp(self):
        self.account = ChartOfAccounts.objects.create(
            account_number='1000',
            account_name='Cash',
            account_type='asset',
            opening_balance=10000.00
        )

    def test_chart_of_accounts_creation(self):
        self.assertTrue(isinstance(self.account, ChartOfAccounts))
        self.assertEqual(self.account.account_name, 'Cash')


class JournalTestCase(TestCase):
    def setUp(self):
        self.journal = Journal.objects.create(
            name='General Journal',
            journal_type='general'
        )

    def test_journal_creation(self):
        self.assertTrue(isinstance(self.journal, Journal))
        self.assertEqual(self.journal.journal_type, 'general')


class BankAccountTestCase(TestCase):
    def setUp(self):
        self.account = BankAccount.objects.create(
            account_name='Main Business Account',
            account_type='checking',
            account_number='123456789',
            bank_name='Test Bank',
            opening_balance=50000.00
        )

    def test_bank_account_creation(self):
        self.assertTrue(isinstance(self.account, BankAccount))
        self.assertEqual(self.account.account_type, 'checking')
