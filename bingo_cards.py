import pickle
import random
import numpy as np 

# this will create specified number of cards and store them on the device 
# so the game master can turn the device off and be able to check if  
# cards already created are winners next time 
# the list of cards will be used in the second script which will start by importing it 

num_cards_to_make = 10000

def make_id(num,num_cards_to_make):
    num_as_str = str(num)
    if len(num_as_str) < len(str(num_cards_to_make)):
        num_as_str = "0" * (len(str(num_cards_to_make))-len(num_as_str)) + num_as_str
    return num_as_str 

def assign_card_id(num_cards_to_make):
    num = 1
    while num < num_cards_to_make+1:
        yield num
        num += 1
card_gen = assign_card_id(num_cards_to_make+1) 

class BingoCard():    

    # instantiate one bingo card - give it an ID and the array of numbers which can be indexed
    def __init__(self):
        SAMP_LEN = 5
        global card_gen
        self.ID = make_id(next(card_gen),num_cards_to_make)

        def choose_letter(start,end):
            x = random.sample(range(start,end),SAMP_LEN)
            return x
        B = choose_letter(1,16)
        I = choose_letter(16,31)
        N = choose_letter(31,46)
        G = choose_letter(46,61)
        O = choose_letter(61,76)

        card = np.array(list(zip(B,I,N,G,O)), 
        dtype = [("B","int32"),("I","int32"), ("N","int32"),
        ("G","int32"), ("O","int32")])
        card["N"][2] = 0 
        self.card = card 

## make multiple cards
cards_list = [BingoCard() for x in range(num_cards_to_make)]

filename = "Cards_List"
outfile = open(filename,"wb")
pickle.dump(cards_list,outfile)