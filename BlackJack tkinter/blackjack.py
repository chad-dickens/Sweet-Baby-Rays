"""BlackJack Game Using tkinter"""

import random
import tkinter
import sqlite3
import datetime


class MainWindow(tkinter.Tk):
    """Class to hold the main tkinter frame that all others sit inside"""
    def __init__(self):
        super().__init__()
        self.width, self.height, self.background = 800, 600, 'green'
        self.geometry('{}x{}'.format(self.width, self.height))
        self.resizable(height=False, width=False)
        self.configure(background=self.background)
        self.title('BlackJack')
        self.create_db()
        self.show_title()
        self.mainloop()

    def show_title(self, current=None):
        """Show title page. If current, will destroy this object"""
        if current:
            current.destroy()
        TitlePage(self, self.width, self.height, self.background)

    def show_leaderboard(self, current):
        """Destroys current frame and displays leaderboard"""
        current.destroy()
        LeaderBoard(self, self.width, self.height, self.background)

    def show_game(self, current):
        """Destroys current frame and displays game"""
        player_name = current.name_entry.get()
        current.destroy()
        GamePage(self, self.width, self.height, self.background, player_name)

    @staticmethod
    def create_db():
        """Creates SQLITE db if one doesn't exist already to store high-scores"""
        conn = sqlite3.connect('blackjack.sqlite')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS high_scores ('
                    'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, '
                    'name TEXT, '
                    'score INTEGER, '
                    'rounds INTEGER, '
                    'date TEXT)')
        conn.commit()
        cur.close()
        conn.close()


class TitlePage(tkinter.Frame):
    """Class for the title page of the game"""
    def __init__(self, parent, width, height, background):
        super().__init__(parent, width=width, height=height, bg=background)

        self.parent = parent

        buffer1 = tkinter.Frame(self, width=width, height=150, background=background)
        buffer1.pack()

        title_label = tkinter.Label(self, text='BlackJack', font=('Garamond', '70'),
                                    background=background, foreground='white')
        title_label.pack()

        buffer2 = tkinter.Frame(self, width=width, height=15, background=background)
        buffer2.pack()

        name_request = tkinter.Label(self, text='Name', font=('Garamond', '15'),
                                     background=background, foreground='white')
        name_request.pack()

        self.name_entry = tkinter.Entry(self, font=('Garamond', '15'))
        self.name_entry.pack()

        self.name_invalid = tkinter.Label(self, text=' ',
                                          font=('Garamond', '15'),
                                          background=background, foreground='red')
        self.name_invalid.pack()

        start_button = tkinter.Button(self, text='Start', font=('Garamond', '30'),
                                      command=self.check_entry)
        start_button.pack()

        leaderboard_button = tkinter.Button(buffer1, text='Leaderboard', font=('Garamond', '12'),
                                            command=lambda: parent.show_leaderboard(self))
        leaderboard_button.place(x=10, y=10)

        self.pack()

    def check_entry(self):
        """Checks that the name entered in is valid.
        If this is the case, the game will be started."""
        if len(self.name_entry.get().strip()) > 0:
            self.name_invalid.configure(text=' ')
            self.parent.show_game(self)
        else:
            self.name_invalid.configure(text='No name provided')


class LeaderBoard(tkinter.Frame):
    """Will display a leaderboard of who has scored the most points"""
    def __init__(self, parent, width, height, background):
        super().__init__(parent, width=width, height=height, bg=background)

        exit_frame = tkinter.Frame(self, width=width, height=30, bg=background)
        exit_button = tkinter.Button(exit_frame, text='Back To Game', font=('Garamond', '12'),
                                     command=lambda: parent.show_title(self))
        exit_button.place(x=10, y=10)
        exit_frame.pack()

        title = tkinter.Label(self, text='Leaderboard', font=('Garamond', '50'),
                              background=background, foreground='white')
        title.pack()

        self.board = tkinter.Frame(self, width=500, height=400, bg='white')
        self.board.pack()
        self.leader_load()

        self.pack()

    def leader_load(self):
        """Populates the leaderboard"""
        col_widths = (10, 180, 280, 380)
        row_height = 10

        # Labels
        font = 'Helvetica 14 bold'
        name_label = tkinter.Label(self.board, text='Name', font=font)
        name_label.place(x=col_widths[0], y=row_height)
        score_label = tkinter.Label(self.board, text='Score', font=font)
        score_label.place(x=col_widths[1], y=row_height)
        round_label = tkinter.Label(self.board, text='Rounds', font=font)
        round_label.place(x=col_widths[2], y=row_height)
        date_label = tkinter.Label(self.board, text='Date', font=font)
        date_label.place(x=col_widths[3], y=row_height)
        row_height += 30

        # Retrieving the high scores from sqlite database
        conn = sqlite3.connect('blackjack.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT name, score, rounds, date '
                    'FROM high_scores '
                    'ORDER BY score DESC '
                    'LIMIT 10;')
        high_scores = cur.fetchall()

        # Putting the data into the table
        font = 'Helvetica 14'
        for num, score in enumerate(high_scores):
            name = tkinter.Label(self.board, text='{}. {}'.format(num + 1, score[0]), font=font)
            name.place(x=col_widths[0], y=row_height)
            player_score = tkinter.Label(self.board, text=str(score[1]), font=font)
            player_score.place(x=col_widths[1], y=row_height)
            rounds = tkinter.Label(self.board, text=str(score[2]), font=font)
            rounds.place(x=col_widths[2], y=row_height)
            date = tkinter.Label(self.board, text=score[3], font=font)
            date.place(x=col_widths[3], y=row_height)
            row_height += 30


class GamePage(tkinter.Frame):
    """The main page where the game is played"""
    def __init__(self, parent, width, height, background, player_name):
        super().__init__(parent, width=width, height=height, bg=background)

        self.parent = parent
        self.player_name = player_name
        self.background = background
        self.round = 0

        dealer_name = tkinter.Label(self, text='Dealer', font='Garamond 50', background='white',
                                    width=width)
        dealer_name.pack()

        self.dealer_score = tkinter.Label(self, text='Score - 0', font='Garamond 14',
                                          background='white', width=width)
        self.dealer_score.pack()

        buffer1 = tkinter.Frame(self, width=width, height=50, bg=background)
        buffer1.pack()

        self.dealer_card_zone = tkinter.Frame(self, width=width, height=107, bg=background)
        self.dealer_card_zone.pack()

        # Displays important information such as who won
        self.message_bar = tkinter.Label(self, text='Round 1', font='Garamond 50',
                                         background=background, foreground='white')
        self.message_bar.pack()

        self.player_card_zone = tkinter.Frame(self, width=width, height=107, bg=background)
        self.player_card_zone.pack()

        buffer2 = tkinter.Frame(self, width=width, height=10, bg=background)
        buffer2.pack()

        self.button_zone = tkinter.Frame(self, width=width, height=75, bg=background)
        self.button_zone.pack()

        buffer3 = tkinter.Frame(self, width=width, height=10, bg=background)
        buffer3.pack()

        # Where player's name is displayed
        player_display = tkinter.Label(self, text=player_name, font='Garamond 50',
                                       background='white', width=width)
        player_display.pack()

        self.player_score = tkinter.Label(self, text='Score - 0', font='Garamond 14',
                                          background='white', width=width)
        self.player_score.pack()

        # Creating players
        self.player = Player(self.player_card_zone, self.player_score, self)
        self.dealer = Player(self.dealer_card_zone, self.dealer_score, self)

        # Saving the back of card image into memory
        self.card_back_image = tkinter.PhotoImage(file='back.png')
        self.card_back_label = tkinter.Label(self.dealer_card_zone, image=self.card_back_image,
                                             background=background)

        # To control the size of buttons
        self.pixel = tkinter.PhotoImage(width=160, height=60)
        # Buttons required. padx of 10 required.
        self.hit_button = tkinter.Button(self.button_zone, text="Hit", font='Garamond 35',
                                         image=self.pixel, compound="c",
                                         command=self.player.deal_card)
        self.stand_button = tkinter.Button(self.button_zone, text="Stand", font='Garamond 35',
                                           image=self.pixel, compound="c",
                                           command=self.play_dealer_hand)
        self.quit_button = tkinter.Button(self.button_zone, text="Quit", font='Garamond 35',
                                          image=self.pixel, compound="c", command=self.quit)
        self.new_game_button = tkinter.Button(self.button_zone, text="New Game",
                                              font='Garamond 35', image=self.pixel, compound="c",
                                              command=self.new_game)
        self.hit_button.pack(side='left', padx=10)
        self.pack()

        # Deal hands to start game
        self.deal_hands()

    def deal_hands(self):
        """Deals cards for the beginning of a new round"""
        self.round += 1
        self.message_bar.configure(text='Round {}'.format(self.round))
        self.hit_button.pack(side='left', padx=10)
        self.stand_button.pack(side='left', padx=10)
        Deck.load_cards()
        self.player.deal_card()
        self.dealer.deal_card()
        self.player.deal_card()
        self.card_back_label.pack(side='left', padx=10)

        # Getting the details for the 4th card
        card_back_details = Deck.deal()
        # Adding this card to dealers hand
        self.dealer.card_list.append(card_back_details[0])
        self.dealer.evaluate_hand()
        image = tkinter.PhotoImage(file=card_back_details[1])
        self.dealer.card_images.append(image)

    def evaluate_winner(self):
        """Determines who won the hand"""
        if self.player.hand_value == 21:
            self.message_bar.configure(text='21. You win.')
            self.player.update_score()
        elif self.player.hand_value > 21:
            self.message_bar.configure(text='Bust. Dealer wins.')
            self.dealer.update_score()
        elif self.dealer.hand_value > 21:
            self.message_bar.configure(text='Dealer bust. You win!')
            self.player.update_score()
        elif self.dealer.hand_value > self.player.hand_value:
            self.message_bar.configure(text='{} to {}. Dealer wins.'
                                       .format(self.dealer.hand_value, self.player.hand_value))
            self.dealer.update_score()
        elif self.dealer.hand_value < self.player.hand_value:
            self.message_bar.configure(text='{} to {}. You win!.'
                                       .format(self.player.hand_value, self.dealer.hand_value))
            self.player.update_score()
        elif self.dealer.hand_value == self.player.hand_value:
            self.message_bar.configure(text='Scores are equal. Dealer wins.')
            self.dealer.update_score()

        # Removing old buttons and putting new buttons in
        self.hit_button.pack_forget()
        self.stand_button.pack_forget()
        self.new_game_button.pack(side='left', padx=10)
        self.quit_button.pack(side='left', padx=10)

    def play_dealer_hand(self):
        """Plays the dealers turn and determines the winner if the dealer hasn't bust"""
        self.card_back_label.pack_forget()
        # Putting the fourth card down onto the table
        tkinter.Label(self.dealer_card_zone, image=self.dealer.card_images[-1],
                      bg=self.background).pack(side='left', padx=5)

        while self.dealer.hand_value < self.player.hand_value and self.dealer.hand_value < 17:
            self.dealer.deal_card()

        # This is here because if the dealer has 21 or greater this method will have already been
        # called
        if self.dealer.hand_value < 21:
            self.evaluate_winner()

    def quit(self):
        """Records players score and returns to title page"""
        conn = sqlite3.connect('blackjack.sqlite')
        cur = conn.cursor()
        cur.execute('INSERT INTO high_scores '
                    '(name, score, rounds, date) '
                    'VALUES (?, ?, ?, ?)', (self.player_name,
                                            self.player.game_score - self.dealer.game_score,
                                            self.round,
                                            datetime.datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        cur.close()
        conn.close()
        self.parent.show_title(self)

    def new_game(self):
        """Clears players hands and prepares the table for another game"""
        self.new_game_button.pack_forget()
        self.quit_button.pack_forget()

        # Removing the cards off the table
        for widget in self.dealer_card_zone.winfo_children():
            widget.pack_forget()

        for widget in self.player_card_zone.winfo_children():
            widget.pack_forget()

        self.player.clear()
        self.dealer.clear()
        self.deal_hands()


class Deck:
    """Class to Hold the 52 cards of the deck"""
    _cards = []

    @classmethod
    def load_cards(cls):
        """
        Loads the names of all 52 cards into memory and then shuffles the deck.
        Card PNG images should be located in the same folder as this module.
        """
        suits = ['heart', 'club', 'spade', 'diamond']
        face_cards = ['jack', 'queen', 'king']
        extension = 'png'
        cls._cards = []

        for suit in suits:
            for i in range(1, 11):
                image_name = '{}_{}.{}'.format(str(i), suit, extension)
                cls._cards.append((i, image_name))

            val = 10
            for i in face_cards:
                image_name = '{}_{}.{}'.format(i, suit, extension)
                cls._cards.append((val, image_name))

        random.shuffle(cls._cards)

    @classmethod
    def deal(cls):
        """Pops a card off the deck"""
        return cls._cards.pop()


class Player:
    """Class to store methods for players"""

    def __init__(self, card_zone, score_zone, parent):
        self.game_score = 0
        self.hand_value = 0
        self.card_list = []
        self.card_images = []
        self.card_zone = card_zone
        self.score_zone = score_zone
        self.parent = parent

    def clear(self):
        """Clears cards from players hand"""
        self.hand_value = 0
        self.card_list = []
        self.card_images = []

    def evaluate_hand(self):
        """Determines the value of current hand"""
        self.hand_value = sum(self.card_list)
        # This works because you can't ever hold more than one 11 in your hand at once
        if 1 in self.card_list and self.hand_value <= 11:
            self.hand_value += 10

    def update_score(self):
        """Adds 1 to players score and updates the screen"""
        self.game_score += 1
        self.score_zone.configure(text='Score - {}'.format(self.game_score))

    def deal_card(self):
        """Deals card from deck, places it on table, and updates hand"""
        card = Deck.deal()
        self.card_list.append(card[0])
        image = tkinter.PhotoImage(file=card[1])
        self.card_images.append(image)
        tkinter.Label(self.card_zone, image=self.card_images[-1],
                      background='green').pack(side='left', padx=5)

        self.evaluate_hand()

        # Checking if player has won or bust
        if self.hand_value >= 21:
            self.parent.evaluate_winner()


if __name__ == '__main__':
    main_window = MainWindow()
