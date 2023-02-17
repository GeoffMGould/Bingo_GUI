from tkinter import *
from tkinter import ttk, font
from tkinter.messagebox import askyesno, showinfo
from PIL import ImageTk, Image
import random
import numpy as np
import re 
import pickle 

class BingoApp:
    def __init__(self,root):
        # retrieves previously saved bingo cards formed in the bingo_cards script
        class CustomUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if name == 'Manager':
                    from settings import Manager
                    return Manager
                return super().find_class(module, name)
        self.cards_list = CustomUnpickler(open("Cards_List","rb")).load()


        self.num_cards_to_make = len(self.cards_list) # used for reference later

        # generator yielding randomized bingo balls (1-75). Reset at the beginning of each game 
        self.game_balls = list(range(1,76))
        random.shuffle(self.game_balls)
        self.game_generator = (ball for ball in self.game_balls)
        self.played_balls = [] # used to check for winners and display played balls to game master and players
        
        # initialize main frame
        root.title("Bingo!")
        
        mainframe = ttk.Frame(root, padding = "3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # initialize string variables
        self.ball_shown = StringVar()
        self.b_balls = StringVar(); self.i_balls = StringVar(); self.n_balls = StringVar()
        self.g_balls = StringVar(); self.o_balls = StringVar()
        self.game_type = StringVar()

        letters_bold = font.Font(weight='bold')
        last_ball_font = font.Font(size=18)

        # Gamemaster window widgets

        self.card_number = StringVar()
        self.card_entry = ttk.Entry(mainframe, width=5, textvariable=self.card_number)
        self.card_entry.grid(column=6,row=1)

        ttk.Label(mainframe, text="Last Ball",font=last_ball_font).grid(column=3,row=4, sticky=W)
        ttk.Label(mainframe,textvariable=self.ball_shown,font=last_ball_font).grid(column=4,row=4, sticky=(W))

        ttk.Label(mainframe, text="Enter Card #").grid(column=5, row=1, sticky=W)

        self.winner = StringVar()
        self.is_winner = ttk.Label(mainframe,textvariable=self.winner).grid(row=1, column=8, columnspan=3, sticky=(W))
        ttk.Button(mainframe, text = "Check", command = self.check_winner).grid(row=1, column=7)

        ttk.Button(mainframe, text = "Clear", command = self.clear_entry).grid(row=2, column=7)

        style = ttk.Style()
        style.configure("W.TButton",bg= "black", font = ("Arial", "14", "bold"), foreground = "blue")
        ttk.Button(mainframe, text = "Next Ball", style="W.TButton", command = self.next_ball).grid(row=2, column=4)

        ttk.Label(mainframe, text="Game Type:").grid(column=9,row=2)
        
        self.game = ttk.Combobox(mainframe, textvariable=self.game_type)
        self.game.grid(row=2,column=10)
        self.game['values']= ("Regular", "X", "Double Postage Stamp","Four Corners", "Picture Frame" ,"Cover All")
        self.game['state']= "readonly" 

        ttk.Label(mainframe, text="B:").grid(column=1,row=6, sticky=W)
        ttk.Label(mainframe,textvariable=self.b_balls, font=letters_bold).grid(column=2,row=6, columnspan=10, sticky=(W))

        ttk.Label(mainframe, text="I:").grid(column=1,row=7, sticky=W)
        ttk.Label(mainframe,textvariable=self.i_balls, font=letters_bold).grid(column=2,row=7, columnspan=10, sticky=(W))

        ttk.Label(mainframe, text="N:").grid(column=1,row=8, sticky=W)
        ttk.Label(mainframe,textvariable=self.n_balls, font=letters_bold).grid(column=2,row=8, columnspan=10, sticky=(W))

        ttk.Label(mainframe, text="G:").grid(column=1,row=9, sticky=W)
        ttk.Label(mainframe,textvariable=self.g_balls, font=letters_bold).grid(column=2,row=9, columnspan=10, sticky=(W))

        ttk.Label(mainframe, text="O:").grid(column=1,row=10, sticky=W)
        ttk.Label(mainframe,textvariable=self.o_balls, font=letters_bold).grid(column=2,row=10, columnspan=10, sticky=(W))

        ttk.Button(mainframe, text = "End Game", command = self.end_game).grid(row=3, column=9)

        # Player window & widgets 

        player= Toplevel()
        player.geometry("500x250")
        player.title("Player")
        player_frame = ttk.Frame(player, padding = "3 3 12 12")
        player_frame.grid(column=0, row=0, sticky=(N,W,E,S))

    

        ttk.Label(player_frame, text="Last Ball",font=last_ball_font).grid(column=3,row=4, sticky=W)
        ttk.Label(player_frame,textvariable=self.ball_shown,font=last_ball_font).grid(column=4,row=4, sticky=(W))

        ttk.Label(player_frame, text="B:").grid(column=1,row=6, sticky=W)
        ttk.Label(player_frame,textvariable=self.b_balls, font=letters_bold).grid(column=2,row=6, columnspan=10, sticky=(W))

        ttk.Label(player_frame, text="I:").grid(column=1,row=7, sticky=W)
        ttk.Label(player_frame,textvariable=self.i_balls, font=letters_bold).grid(column=2,row=7, columnspan=10, sticky=(W))

        ttk.Label(player_frame, text="N:").grid(column=1,row=8, sticky=W)
        ttk.Label(player_frame,textvariable=self.n_balls, font=letters_bold).grid(column=2,row=8, columnspan=10, sticky=(W))

        ttk.Label(player_frame, text="G:").grid(column=1,row=9, sticky=W)
        ttk.Label(player_frame,textvariable=self.g_balls, font=letters_bold).grid(column=2,row=9, columnspan=10, sticky=(W))

        ttk.Label(player_frame, text="O:").grid(column=1,row=10, sticky=W)
        ttk.Label(player_frame,textvariable=self.o_balls, font=letters_bold).grid(column=2,row=10, columnspan=10, sticky=(W))

        ttk.Label(player_frame, text = "Game Type: ").grid(column=3, row=1, sticky=(E))
        ttk.Label(player_frame, textvariable=self.game_type).grid(column=4, row=1, sticky=(E))

    # functions 
    def make_id(self,num,num_cards_to_make):
        """ PADS CARD # WITH 0'S TO MAKE LENGTH UNIFORM"""
        num_as_str = str(num)
        if len(num_as_str) < len(str(self.num_cards_to_make)):
            num_as_str = "0" * (len(str(self.num_cards_to_make))-len(num_as_str)) + num_as_str
        return num_as_str 

    def reset_game(self):
        """RESTARTS GENERATOR OF BALLS AND CLEARS ALL LISTS OF PLAYED BALLS"""
        random.shuffle(self.game_balls)
        self.game_generator = (ball for ball in self.game_balls)
        self.played_balls = []
        

    def next_ball(self):
        """SELECTS NEXT BALL FROM GENERATOR, UPDATES LIST OF BALLS PLAYED,
        AND DISPLAYS LAST BALL DRAWN"""
        self.played_balls.append(next(self.game_generator))
        if self.played_balls[len(self.played_balls)-1] < 16:
            self.ball_shown.set("B-"+str(self.played_balls[len(self.played_balls)-1]))
        elif 16 <= self.played_balls[len(self.played_balls)-1] <= 30:
            self.ball_shown.set("I-"+str(self.played_balls[len(self.played_balls)-1]))
        elif 31 <= self.played_balls[len(self.played_balls)-1] <= 45:
            self.ball_shown.set("N-"+str(self.played_balls[len(self.played_balls)-1]))    
        elif 46 <= self.played_balls[len(self.played_balls)-1] <= 60:
            self.ball_shown.set("G-"+str(self.played_balls[len(self.played_balls)-1]))    
        elif 61 <= self.played_balls[len(self.played_balls)-1]:
            self.ball_shown.set("O-"+str(self.played_balls[len(self.played_balls)-1]))    

        pb_arr = np.array(sorted(self.played_balls))
        b_array = pb_arr[pb_arr<16]; b_mod = b_array.astype(str)
        i_array = pb_arr[(pb_arr > 15) & (pb_arr < 31)]; i_mod = i_array.astype(str)
        n_array = pb_arr[(pb_arr > 30) & (pb_arr < 46)]; n_mod = n_array.astype(str)
        g_array = pb_arr[(pb_arr > 45) & (pb_arr < 61)]; g_mod = g_array.astype(str)
        o_array = pb_arr[pb_arr > 60]; o_mod = o_array.astype(str)
         
        # for nicer formatting of played balls, put space in between integers
        add_space = np.vectorize(lambda x : x + " ")
        if len(b_mod) > 0:
            self.b_balls.set(np.array2string(add_space(b_mod),separator=" ", formatter = {'str_kind': lambda x: x}))
        if len(i_mod) > 0:    
            self.i_balls.set(np.array2string(add_space(i_mod),separator=" ", formatter = {'str_kind': lambda x: x}))
        if len(n_mod) > 0:    
            self.n_balls.set(np.array2string(add_space(n_mod),separator=" ", formatter = {'str_kind': lambda x: x}))
        if len(g_mod) > 0:    
            self.g_balls.set(np.array2string(add_space(g_mod),separator=" ", formatter = {'str_kind': lambda x: x}))
        if len(o_mod) > 0:    
            self.o_balls.set(np.array2string(add_space(o_mod),separator=" ", formatter = {'str_kind': lambda x: x}))

        if self.winner.get() == "Not a winner":
            self.winner.set("")
            
    def check_winner(self):  
        """WHEN SOMEONE CALLS BINGO, GAME MASTER INPUTS CARD #. FUNCTION CAN LOOK UP THE NUMBERS
        ON THE CARD, MATCH IT WITH BALLS PLAYED, AND CHECK THIS AGAINST GAME TYPE TO SEE IF CALL
        IS VALID"""
        
        potential_winner = self.card_number.get()
        pot_win_ID = self.make_id(potential_winner,self.num_cards_to_make)
        game_style = self.game_type.get()

        # prevents incorrect input (number higher than # of cards made)
        if re.search("^\d+$",pot_win_ID):      
            if int(pot_win_ID) > self.num_cards_to_make:
                self.winner.set(" Number is too high - try again")
                self.card_entry.delete(0,END)     

        # prevents incorrect input (anything other than digits up to length of # of cards made)
        if not re.search("^\d{{1,{0}}}$".format(str(len(str(self.num_cards_to_make)))),pot_win_ID): 
            self.winner.set(" Input error - must be numbers only")
            self.card_entry.delete(0,END)  

        else:    
            try:
                card_to_check = next((x for x in self.cards_list if x.ID == pot_win_ID), None).card
              
                if game_style == "X":
                    if (card_to_check["B"][0] in self.played_balls) & (card_to_check["I"][1] in self.played_balls) & \
                    (card_to_check["G"][3] in self.played_balls) & (card_to_check["O"][4] in self.played_balls ) & \
                    (card_to_check["B"][4] in self.played_balls) & (card_to_check["I"][3] in self.played_balls) & \
                    (card_to_check["G"][1] in self.played_balls) & (card_to_check["O"][0] in self.played_balls):
                        self.winner.set("Winner!")
                        self.reset_game()      
                    else:
                        self.winner.set("Not a winner")
                        self.card_entry.delete(0,END) 

                elif game_style == "Four Corners":
                    if (card_to_check["B"][0] in self.played_balls) & (card_to_check["B"][4] in self.played_balls) & \
                        (card_to_check["O"][0] in self.layed_balls) & (card_to_check["O"][4] in self.played_balls):
                        self.winner.set("Winner!")
                        self.reset_game()
                    else:
                        self.winner.set("Not a winner")
                        card_entry.delete(0,END)   

                elif game_style == "Picture Frame":
                    if (all(item in self.played_balls for item in list(card_to_check["B"]))) & \
                    (all(item in self.played_balls for item in list(card_to_check["O"]))) & \
                    (all(item in self.played_balls for item in list(card_to_check[0]))) & \
                    (all(item in self.played_balls for item in list(card_to_check[4]))):
                        self.winner.set("Winner!")
                        self.reset_game()
                    else:
                        self.winner.set("Not a winner")
                        self.card_entry.delete(0,END)  

                elif game_style == "Cover All":
                    n_list = list(card_to_check["N"]) # accounts for free space
                    n_list.remove(0)

                    if (all(item in self.played_balls for item in list(card_to_check["B"]))) & \
                    (all(item in self.played_balls for item in list(card_to_check["I"]))) & \
                    (all(item in self.played_balls for item in n_list)) & \
                    (all(item in self.played_balls for item in list(card_to_check["G"]))) & \
                    (all(item in self.played_balls for item in list(card_to_check["O"]))):
                        self.winner.set("Winner!")
                        self.reset_game()
                    else:
                        self.winner.set("Not a winner")
                        self.card_entry.delete(0,END)     

                elif game_style == "Double Postage Stamp":
                    nw_corner = [card_to_check["B"][0],card_to_check["B"][1],card_to_check["I"][0],card_to_check["I"][1]]
                    sw_corner = [card_to_check["B"][3],card_to_check["B"][4],card_to_check["I"][3],card_to_check["I"][4]]
                    ne_corner = [card_to_check["G"][0],card_to_check["G"][1],card_to_check["O"][0],card_to_check["O"][1]]
                    se_corner = [card_to_check["G"][3],card_to_check["G"][4],card_to_check["O"][3],card_to_check["O"][4]]
                    if ((all(item in self.played_balls for item in nw_corner + sw_corner))) | \
                    ((all(item in self.played_balls for item in nw_corner + ne_corner))) | \
                    ((all(item in self.played_balls for item in nw_corner + se_corner))) | \
                    ((all(item in self.played_balls for item in sw_corner + ne_corner))) | \
                    ((all(item in self.played_balls for item in sw_corner + se_corner))) | \
                    ((all(item in self.played_balls for item in ne_corner + se_corner))):
                        self.winner.set("Winner!")
                        self._game()
                    else:
                        self.winner.set("Not a winner")
                        self.card_entry.delete(0,END) 


                elif game_style == "Regular":  
                    n_list = list(card_to_check["N"]) # accounts for free space
                    n_list.remove(0)

                    third_row = list(card_to_check[2])
                    third_row.remove(0) # accounts for free space

                    if (all(item in self.played_balls for item in list(card_to_check["B"]))) | \
                    (all(item in self.played_balls for item in list(card_to_check["I"]))) | \
                    (all(item in self.played_balls for item in n_list)) | \
                    (all(item in self.played_balls for item in list(card_to_check["G"]))) | \
                    (all(item in self.played_balls for item in list(card_to_check["O"]))) | \
                    (all(item in self.played_balls for item in list(card_to_check[0]))) | \
                    (all(item in self.played_balls for item in list(card_to_check[1]))) | \
                    (all(item in self.played_balls for item in third_row)) | \
                    (all(item in self.played_balls for item in list(card_to_check[3]))) | \
                    (all(item in self.played_balls for item in list(card_to_check[4]))) | \
                    ((card_to_check["B"][0] in self.played_balls) & (card_to_check["I"][1] in played_balls) & \
                    (card_to_check["G"][3] in self.played_balls) & (card_to_check["O"][4] in played_balls)) | \
                    ((card_to_check["B"][4] in self.played_balls) & (card_to_check["I"][3] in played_balls) & \
                    (card_to_check["G"][1] in self.played_balls) & (card_to_check["O"][0] in played_balls)):
                        self.winner.set("Winner!")
                        self.reset_game()
                    else:
                        self.winner.set("Not a winner")
                        self.card_entry.delete(0,END)  

                else:  
                    self.winner.set("Please select a game type from the menu")  
            # catches any other incorrect input (such as "0")        
            except:
                self.winner.set("Invalid Entry")
                self.card_entry.delete(0,END)       
                    
                    
    def end_game(self):
        """GIVES GAME MASTER OPTION TO END GAME AND THEN ASKS TO CONFIRM CHOICE"""
        answer = askyesno(title = "End Game?", message = "Are you sure you want to end the current game?") 

        if answer: # clear variables
            self.b_balls.set(""); self.i_balls.set(""); self.n_balls.set(""); self.g_balls.set(""),self.o_balls.set("")
            self.ball_shown.set("")
            self.winner.set("")
            self.reset_game()
        else: 
            showinfo("Continue Game", "The game will now continue")            
            
    def clear_entry(self):
        """CLEARS ERROR MESSAGES OR WINNER DECLARATIONS"""
        self.winner.set("")

root = Tk()   
BingoApp(root)
root.mainloop()
   

