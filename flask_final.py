from flask import Flask, redirect, url_for, request
from naiveBayesClassifier import tokenizer
from naiveBayesClassifier.trainer import Trainer
from naiveBayesClassifier.classifier import Classifier

import nltk, re,      pprint
from nltk import word_tokenize, sent_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import enchant
import json


import sys

try:
	import urllib.request as urllib2
except ImportError:
    import urllib2
import urllib
import webbrowser
from bs4 import BeautifulSoup

#sentences = "the barking dogs seldom bite. But the dogs which are silent may bite you. Dogs are silent animals and human's best friend. They are very faithful and loyal to their masters. They eat whatever is given to them and don't throw tantrums."
#sentences = "the black dog is very wild. It bites lot of people. Many people then have to got to hospitals. They get angry from this dog."

#sentences = "United States is a thief. He spends lot of money on his car. His car name is Vai."
#sentences = "Carbon is a chemical element with symbol C and atomic number 6. On the periodic table, it is the first (row 2) of six elements in column (group 14), which have in common the composition of their outer electron shell. It is nonmetallic and tetravalent—making four electrons available to form covalent chemical bonds. Three isotopes occur naturally, 12C and 13C being stable while 14C is radioactive, decaying with a half-life of about 5,730 years. Carbon is one of the few elements known since antiquity."
#sentences = "i usually have 5 different stopwords list per classification project, each of which grows as the algorithm is re-optimized and tweaked throughout the life-time of the project, in order for the classifier to meet the target accuracy figure, some of the stopwords list include:"
#sentences = "this is United States and i love it and your motherland"
#sentences = "The sad dog is hot and this is cool, really cool. He is barking talking about the United States and covalent bonds. The chemical reactions between them is so so fascinating. This is Sherlock Holmes."


def gen(text):
    token = nltk.word_tokenize(text)
    bigrams = nltk.ngrams(token, 2)
    return "-->".join(map(" ".join, bigrams))

bigramList = ['periodic table', 'atomic mass', 'atomic number', 'atomic weight', 'covalent bonds', 'United States', 'chemical bonds' , 'ionic bonds', 'chemical reactions', 'chemical reaction', 'Sherlock Holmes', 'Baker Street', 'Doctor Watson']

suffix = ['ed','d','ing']

b = list()
c = list()

remTup = list()

subject = dict()



newList = list()

wnl = WordNetLemmatizer()






def proceed(sentences):
    currentSubject = ''
    sentences = sent_tokenize(sentences)

    for sentence in sentences:
    
        tokenized = word_tokenize(sentence)
        bigrams = ''

        # the making of the bigram list''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
        bigrams = gen(sentence)
        bigramsList = list()
        bigramsList[0:len(bigramsList)+1] = []
        newList[0:len(newList)+1] = []

        newTaggedList = list()
        newTaggedList[0:len(newTaggedList)+1] = []
        bigramsList = bigrams.split("-->")

        x = 0

        for i in bigramsList:
        
            if  i in bigramList:
        
                j = i.split(" ")
           
                for k in range(len(tokenized)-1):
                    if tokenized[k] == j[0] and tokenized[k+1] == j[1]:
                    
                        newList.append((tokenized[k] + " " + tokenized[k+1]))
                        if (bigramsList.index(i)+1) < len(bigramsList):
                            bigramsList.pop((bigramsList.index(i))+1)
                        x += 2

            else:
                newList.append(tokenized[x])
                if (bigramsList.index(i) == (len(bigramsList)-1)):
                    newList.append(tokenized[x+1])
                x += 1
       
    
        newTaggedList = pos_tag(newList)

        remTup[0:len(remTup)+1] = []
        for i in range(len(newTaggedList)):
            remTup.append(list(newTaggedList[i]))

        print (remTup)
        print ("that was remTup printing")

        # the correction of POStagging starts here............................................................................

        for i in range(len(remTup)):
            if len(remTup[i][0].split()) > 1:
                if remTup[i][0] in bigramList and remTup[i][1][0] != 'N':
                    remTup[i][1] = 'NN'



        k = 0
        if remTup[k][1] != 'PRP' and remTup[k+1][1][0] != 'V':
            while(remTup[k][1][0] != 'N'):
                if (remTup[k][1][0] != 'D'):
                    remTup[k][1] = 'JJ'
                k += 1

        if remTup[k][1] == 'PRP' and remTup[k+1][1] == 'CC' and remTup[k+2][1][0] == 'N':
            k = k+2
            while(remTup[k][1][0] != 'N'):
                if (remTup[k][1][0] != 'D'):
                    remTup[k][1] = 'JJ'
                k += 1
        d = enchant.Dict("en_US")
        for i in range(len(remTup)):
            for suff in suffix:
                if remTup[i][0].endswith(suff):
               
                    tent = remTup[i][0]
                    tent = re.sub(suff, '', tent)
                    if (d.check(tent) == True):
                        remTup[i][1] = 'VB'
                        break
                    else:
                        continue
                else:
                    continue


        for j in range(len(remTup)):
            if remTup[j][0].endswith('ied'):
                ten = re.sub('ied','y',ten)
                if (d.check(tent) == True):
                    remTup[j][1] = 'VB'
                    break
                else:
                    continue
            else:
                continue



        #real pasrding starts here.....................................................

        subject[currentSubject] = 1
        flag = 0
        tentativeSubject = ''
        for i in range(len(remTup)):
       
            if remTup[i][0] == 'is' or remTup[i][0] == 'are' or remTup[i][0] == 'am' or remTup[i][0] == 'was' or remTup[i][0] == 'were':
                flag = 1
            if flag != 1:
                if remTup[i][1][0] == 'N':
                    j = i-1
                    toAppend = ''
                    toAppend = remTup[i][0] + " "
                    while j>0 or remTup[j][1][0] == 'J' or remTup[j][0].endswith('ing'):
                        toAppend = remTup[j][0] + " " + toAppend + " "
                        j -= 1
                    b.append(toAppend)
                    
                    tentativeSubject = tentativeSubject + " " + remTup[i][0]
               
                    if tentativeSubject != currentSubject:
                    
                        currentSubject = tentativeSubject
                if remTup[i][1] == 'PRP':
                
                    if currentSubject in subject:
                        subject[currentSubject] += 1
                    else:
                        subject[currentSubject] = 1

            if (remTup[i][1][0]) == 'N' and remTup[i][0] not in b :
                c.append(remTup[i][0])


    print("the list of subjects is below")
    print (b)

    print ("the list of non subjects nouns is below")
    print (c)


    newsTrainer = Trainer(tokenizer)


    newsSet =[
        {'text': 'weight', 'category': 'health'},
        {'text': 'doctors health professionals patients', 'category': 'health'},
        {'text': 'chocolate diabetes heart diseases', 'category': 'health'},
        {'text': 'AIDS disease', 'category': 'health'},
        {'text': 'protein vitamins minerals balanced_diet', 'category': 'health'},
        {'text': 'cancer', 'category': 'health'},
        {'text': 'Russia Ukraine', 'category': 'politics'},
        {'text': 'exercise', 'category': 'health'},
        {'text': 'Syria Obama', 'category': 'politics'},
        {'text': 'weight', 'category': 'health'},
         {'text': 'sherlock_solmes sherlock', 'category': 'TV_Personalities'},
        {'text': 'element isotope reaction chemical ionic_bond bond periodic_table covalent_bond oxygen carbon nitrogen electron shell half_life', 'category': 'chemistry'},

        {'text': 'cricket table_tennis badminton football soccer rugby baseball snooker basketball volleyball updates tennis ','category':'sports'},
        {'text': 'Sachin-Tendulkar','category':'sports'},
        {'text': 'sun moon mercury venus jupiter mars earth neptune pluto solar_eclipse lunar_eclipse uranus stars light_year planets galaxy milky_way NASA','category': 'space research'},
        {'text': 'eclipse space ISRO ','category': 'space research'}
    
    ]

    for news in newsSet:
        newsTrainer.train(news['text'], news['category'])

    newsClassifier = Classifier(newsTrainer.data, tokenizer)

    print ("before the making of d...............................................")
    l = ['carbon', 'graphite', 'electron', 'proton', 'shell', 'half_life']

    d = list()
    li = list()

    d = b
    print (d)
    print ("real game begins........................")

    
    for item in d:
        if len(item.split()) == 1:
            li.append(item)
        else:
            newBi = gen(item)
            newBiList = newBi.split("-->")
            toApp = ''
            print (newBiList)
            for it in newBiList:
                if it not in bigramList:
                    tent = pos_tag(word_tokenize(it))
                    if tent[0][1][0] != 'N' and tent[1][1][0] == 'N':
                        li.append(tent[1][0])
                    if tent[1][0][0] != 'N' and tent[0][1][0] == 'N':
                        li.append(tent[0][1])
                    newBiList.remove(it)
                else:
                    toAppList = it.split()
                    toApp = toAppList[0] + "_" + toAppList[1]
                    li.append(toApp)
                
    print (li)

    synWordList = list()
    tempList = list()
    synElemList = list()

    tempStrWord = ''
    cutWord = ''
    finalCutWord = ''


    tempStr = ''
    tempElemWord = ''
    cutElemWord = ''

    wnl = WordNetLemmatizer()

    

    for i in range(len(li)):
        li[i] = li[i].replace(" ","")
        li[i] = li[i].lower()
        isp, lemma = isplural(li[i])
        #print (nn, lemma, isp)
        li[i] = lemma

    print ("the updated li is ")
    print (li)




    for word in li:
        classList = newsClassifier.classify(word)
        count = 0
        maxProb = 0.0
        for j in classList:
            if j[1] == 0.0:
                count += 1
            else:
                if j[1]>maxProb:
                    maxProb = j[1]
                    category = j[0]
                    print("the max similarity " + str(maxProb) + " and category " + str(category) + " the word is " + word)


        if count == 6: #word not found
            tempStrWord = ''
            cutWord = ''
            synWordList = wn.synsets(word)
            for iNum in range(len(synWordList)):
                tempStrWord = str(synWordList[iNum])
                cutWord = tempStrWord[8:len(tempStrWord)-7]
           
                if len(cutWord) == len(word):
                    finalCutWord = cutWord + '.n.01'
                else:
                    continue

            maxOne = 0.0
            tempStr = '' 
            tempElumWord = ''
            cutElemWord = ''
            finalElemWord = ''

            for k in range(len(newsSet)):
                tempStr = newsSet[k]['text']
                tempList = tempStr.split()
                for elem in tempList:
                    synElemList = wn.synsets(elem)
                    for elumNum in range(len(synElemList)):
                        tempElumWord = str(synElemList[elumNum])
                        cutElemWord = tempElumWord[8:len(tempElumWord)-7]
                   
                        if elem == cutElemWord:
                            finalElemWord = cutElemWord + '.n.01'
                
                    elemSimi = wn.synset(finalElemWord)
                    wordSimi = wn.synset(finalCutWord)
                    simIndex = wn.wup_similarity(elemSimi, wordSimi)
                    if simIndex > maxOne:
                        maxOne = simIndex
                        updatedCategory = newsSet[k]['category']

            print ("the category is " + updatedCategory + " and the maximum similarity is " + str(maxOne) + " the word is " + word)

    
    str1 = ' '.join(b)

    str2 = str1.replace(" ","+")

    print("words went in search:")
    print(str2)
    url = "https://www.google.co.in/search?q=" +(str(str2))+ "&oq="+(str(str2))
    #webbrowser.open_new(url)
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]


    for start in range(0,1):
        #start variable is for no. of pages to get url #(0,1) for first page only
        url = url + str(start*1)
        page = opener.open(url)
        soup = BeautifulSoup(page)

        
    print("The urls for searched query: ")

    cite_tag = soup.findAll('cite')
    j=0

    len1 = len(cite_tag)
    print("")
    print("Total no. of urls is: ",len1)
    print("")
    jj=""
    kk=""
    ww=""
    for i in range(0,2):

        if(cite_tag[i].text.startswith("https://en.wikipedia.org")):
            print (cite_tag[i].text)
            babr=crawl(cite_tag[i].text,str2)
            jj=jj+"\n"+babr

        elif(cite_tag[i].text.startswith("https://www.youtube")):
            continue

        elif(cite_tag[i].text.startswith("https://twitter.com/")):
            continue

        elif(cite_tag[i].text.startswith("www.")):
            url1="http://"+cite_tag[i].text
            print(url1)
            babt=crawl("http://"+cite_tag[i].text,str2)
            kk=kk+"\n"+babt
            
        elif(cite_tag[i].text.startswith("https:")):
            print(cite_tag[i].text)
            babi=crawl(cite_tag[i].text,str2)
            ww=ww+"\n"+babi

    happy=""
    happy=jj+"\n"+kk+"\n"+ww
    print (happy)
    return happy

def isplural(word):
    lemma = wnl.lemmatize(word, 'n')
    plural = True if word is not lemma else False
    return plural, lemma


def crawl(url,key):

    #ny=wikipedia.page(key)


    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)

  # kill all script and style elements
    for script in soup(["script", "style"]):
        script.decompose()    # rip it out
    
    pq= soup.select('p')

    le=len(pq)
    print(le)
    final=""
    hola=""
    if(le<12 or le==12):
        for i in range(0,le):
   
            print(pq[i].getText())
            final=final+pq[i].getText()
            print("")

        final=final+"\n"+"########################"

    else:

        #print(ny.content)
        
        for i in range(0,12):
            
            try:
                
                print(pq[i].getText())
                #print(pq[i].prettify())
                final=final+pq[i].getText()
                
            except Exception:
                
                print(str(pq[i].get_text().encode('utf-8')))
                print(str(pq[i].prettify().encode('utf-8')))
        final=final+"\n"+"########################"

    return final

      

app = Flask(__name__)

@app.route('/hello', methods = ['POST','GET'])
def world():
    if request.method == 'POST':
        #dic = request.data
        #dic = request.args.get("name")
        data = request.data
        data = data.decode("utf-8")
        myD = dict()
        myD = data
        print (type(myD))
        myDD = dict()
        myDD = json.loads(myD)
        print (myDD)
        print (type(myDD))
        finalStr =  (myDD.get('movie'))
        print (finalStr)
        #print (myD.get("movies"))
        #data = json.loads(data)
        #print (data["movie"])
        #print(data)
        answer = ""
        
        answer = proceed(finalStr)
        #strt = ''.join(answer)
        return answer

    else:
        return "world"


if __name__ == '__main__':
   app.run(debug = True, host = '0.0.0.0')
