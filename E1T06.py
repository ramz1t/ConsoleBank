from os import name, system
from enum import Enum
import re

class Console:
    """
    A class used to print in console with color

    ...

    Methods
    -------
    clear()
        Clears current output in the console
    error(prompt)
        Prints with red color
    info(prompt)
        Prints with blue color
    success(prompt)
        Prints with green color
    print(prompt)
        Prints with default color
    new_line()
        Moves output cursor to new line
    """

    @staticmethod
    def clear():
        system('cls' if name == 'nt' else 'clear')

    @staticmethod
    def error(prompt):
        print(f'\033[91m\033[1m{prompt}\033[0m')

    @staticmethod
    def info(prompt):
        print(f"\033[94m\033[1m-- {prompt} --\n\033[0m")

    @staticmethod
    def success(prompt):
        print(f'\033[92m\033[1m{prompt}\033[0m')
    
    @staticmethod
    def print(prompt):
        print(prompt)

    @staticmethod
    def new_line():
        print()


class UserCommand(Enum):
    DEPOSIT = 1
    WITHDRAW = 2
    CHECK_BALANCE = 3
    ACCOUNT_INFO = 4
    LOG_OUT = 5


class BankCommand(Enum):
    CREATE_CLIENT = 1
    LOGIN = 2
    EXIT = 3


class Client:
    """
    A class used to store and work with single bank client

    ...

    Methods
    -------
    __str__()
        String representation of the client
    deposit()
        Gets the amount to deposit and updates balance
    withdraw()
        Gets the amount to withdraw, checks if it's possible and updates balance
    get_balance()
        Prints the client's current balance
    """

    def __init__(self, name, civic_number, balance, interest_rate) -> None:
        """
        Parameters
        ----------
        name : str
            The name of the client
        civic_number : str
            The client's social security number
        balance : float
            The initial amount of money the client has
        interest_rate : float
            The interest rate of the account
        """

        self.name = name
        self.civic_number = civic_number
        self.balance = balance
        self.interest_rate = interest_rate / 100

    def __str__(self) -> str:
        return f"Name: {self.name}\nCivic number: {self.civic_number}\nBalance: {self.balance:,.2f} SEK\nInterest rate: {self.interest_rate * 100:.2f} %\n\nAfter one year you'll have: {self.balance * (1 + self.interest_rate):,.2f}"

    def deposit(self):
        Console.info("Deposit")
        try:
            new_deposit = float(input("How much money do you want to deposit (SEK)? "))
            if new_deposit < 0:
                Console.error("Deposit can't be negative")
                return
            self.balance += new_deposit
        except ValueError:
            Console.error("Wrong deposit ammount")

    def withdraw(self):
        Console.info("Withdraw")
        try:
            withdrawal_amount = float(input("How much you want to withdraw (SEK)? "))
            if withdrawal_amount > self.balance:
                Console.error("Not enough money")
                return
            if withdrawal_amount < 0:
                Console.error("Withdrawal amount can't be negative")
                return
            self.balance -= withdrawal_amount
        except ValueError:
            Console.error("Wrong withdrawal ammount")

    def get_balance(self):
        Console.print(f"You have {self.balance:,.2f} SEK on your account")


class Bank:
    """
    A class used to store and work with single bank client

    ...

    Methods
    -------
    create_client()
        Creates and adds the new client
    list_clients()
        List all the bank's clients with indexes
    """

    def __init__(self) -> None:
        self.clients = []

    def validate_luhn(self, civic_number) -> str:
        """
        Checks if the given civic number is a valid luhn number

        ...

        Parameters
        ----------
        civic_number : int
            Client's civic number
        
        Raises
        ------
        ValueError
            If the civic_number is invalid

        Returns
        -------
        str
            A validated and cleared civic number
        """

        if not (re.match(r'^\w{6}-\w{4}$', civic_number) 
                or re.match(r'^\w{8}-\w{4}$', civic_number)
                or re.match(r'^\w{12}$', civic_number)
                or re.match(r'^\w{10}$', civic_number)):
            raise ValueError
        
        civic_number = civic_number.replace('-', '')

        if len(civic_number) == 12:
            civic_number = civic_number[2:]
        
        checksum_string = ""

        for index, digit in enumerate(civic_number[:-1]):
            checksum_string += str(int(digit) * (2 - index % 2))
        
        checksum = sum([int(s) for s in checksum_string])
        check_digit = (10 - checksum % 10) % 10

        if str(check_digit) != civic_number[-1]:
            raise ValueError
        
        civic_number = civic_number[:6] + '-' + civic_number[6:]
        return civic_number
        

    def create_client(self):
        Console.info("Registering new client")

        try:
            name = input("Please enter your name: ").capitalize()
            civic_number = input("Please enter your civic number: ")
            balance = float(input("Please enter how much money you have: "))
            interest_rate = int(input("Please enter the interest rate in percent: "))
        except ValueError:
            Console.error("Wrong input")
            return
        
        try:
            civic_number = self.validate_luhn(civic_number)
        except ValueError:
            Console.error("Wrong civic number")
            return
        
        if balance < 0 or interest_rate < 0:
            Console.error("Balance and interest rate must be positive")
            return
        
        client = Client(name=name, civic_number=civic_number, balance=balance, interest_rate=interest_rate)
        self.clients.append(client)

    def list_clients(self):
        for index, client in enumerate(self.clients):
            print(f"{index + 1}. {client.name}")


class BankApp:
    """
    A class for console bank app

    ...

    Methods
    -------
    run()
        Runs the app
    handle_authenticated_user()
        Event handler for authenticated user commands
    handle_guest_user()
        Event handlser for main menu (without auth)
    login_user()
        Lists all the bank users and ask a user to choose acc
    get_user_input()
        Gets and validates user command input
    """

    def __init__(self, name):
        """
        Parameters
        ----------
        name : str
            The name of the console bank
        """

        self.name = name
        self.bank = Bank()
        self.command = None
        self.current_user = None
        self.is_running = True

    def run(self):
        Console.clear()
        Console.success(f"Welcome to {self.name}!\n")
        while self.is_running:
            if self.current_user:
                self.handle_authenticated_user()
            else:
                self.handle_guest_user()
            Console.new_line()
        Console.success(f"Thank you for using {self.name}!")
    
    def handle_authenticated_user(self):
        self.command = self.get_user_input("Select operation:\n1. Deposit\n2. Withdraw\n3. Check balance\n4. Account info\n5. Log out\n")
        match self.command:
            case UserCommand.DEPOSIT.value:
                self.current_user.deposit()
            case UserCommand.WITHDRAW.value:
                self.current_user.withdraw()
            case UserCommand.CHECK_BALANCE.value:
                self.current_user.get_balance()
            case UserCommand.ACCOUNT_INFO.value:
                Console.print(self.current_user)
            case UserCommand.LOG_OUT.value:
                self.current_user = None
            case _:
               Console.error("Invalid operation, try again")

    def handle_guest_user(self):
        self.command = self.get_user_input("Select operation:\n1. Create a client\n2. Login to online-bank\n3. Exit\n")
        match self.command:
            case BankCommand.CREATE_CLIENT.value:
                self.bank.create_client()
            case BankCommand.LOGIN.value:
                self.login_user()
            case BankCommand.EXIT.value:
                self.is_running = False
            case _:
               Console.error("Invalid operation, try again")

    def login_user(self):
        Console.info("Login")
        if len(self.bank.clients) > 0:
            Console.print("Select an account:")
            self.bank.list_clients()
            selection = self.get_user_input()
            if selection:
                if 1 <= selection <= len(self.bank.clients):
                    self.current_user = self.bank.clients[selection - 1]
                else:
                    Console.error("Account doesn't exist")
            else:
                Console.error("Wrong selection")
        else:
            Console.error("You need to create an account first")

    def get_user_input(self, prompt=""):
        try:
            user_input = int(input(prompt))
            Console.clear()
            return user_input
        except ValueError:
            Console.error("Invalid input, please enter a number.")
            return None


app = BankApp(name="HKR Bank")
app.run()