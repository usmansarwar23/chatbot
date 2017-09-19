from googletrans.client import Translator

#----- TAKE INPUT -----#

input_list = input('Enter a phrase: ').split()	#class: list. ['str','str']


#----- LOAD URDU DATASET FOR NORMALIZATION -----#

file1 = open("norm_urdu.csv", encoding = "utf8")
file = list(file1)	#saves dataset as list


#----- NORMALIZE INPUT -----#

out_list = ""
i = 0
while i < len(input_list):
    word = input_list[i]							
    out_word = 0	#to store a normalized word in following loop (if any)
    for line in file:	#checks every line of the urdu dataset against the 'word'
        line = line.split(",")
        for value in line:	#value = word of a line of the dataset
            if word == value:	#checks if word is present in the respective line of the dataset
                if out_list == "":
                    out_list = out_list + line[0]
                else:
                    out_list = out_list + " " + line[0]
                #out_list.append(line[0])
                out_word = line[0]
                #print (out_word)
                break
    if out_word == 0:	#if word is not present in the dataset for normalization, save it to the out_list as it is
        #out_list.append(word)
        if out_list == "":
            out_list = out_list + word
        else:
            out_list = out_list + " " + word
        #print (word)
    i = i+1
print ("Input: ",out_list)	#prints normalized input


#----- GOOGLE TRANSLATE INPUT -----#

translator = Translator()
trans_input = translator.translate(out_list).text
print("Translated Input: ", trans_input)	#prints translated input


#----- ASSIGN TO RASA_NLU -----#

#Training Time
from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.model import Trainer

builder = ComponentBuilder(use_cache=True)	#will cache components between pipelines (where possible)
training_data = load_data('testData.json')
trainer = Trainer(RasaNLUConfig("config_spacy.json"), builder)
trainer.train(training_data)
model_directory = trainer.persist('./models/')	#returns the directory the model is stored in

#Prediction Time
from rasa_nlu.model import Metadata, Interpreter
config = RasaNLUConfig("config_spacy.json")

metad = Metadata.load(model_directory)	#loads metadata.json
interpreter = Interpreter.load(metad, config, builder)

interpreter.parse(trans_input)	#output
