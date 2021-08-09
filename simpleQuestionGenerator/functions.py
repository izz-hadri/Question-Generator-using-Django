'''
pip install wheel
pip install nltk
pip install yake
pip install flashtext==2.7
pip install transformers==4.9.0
pip install sentencepiece==0.1.96
pip install pytorch-lightning==1.3.8
pip install torchtext==0.10.0

'''
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from flashtext import KeywordProcessor
from transformers import T5ForConditionalGeneration, T5Tokenizer
import random
import torch
import yake
import nltk
nltk.download('wordnet')
nltk.download('punkt')


def tokenize_sentences(text):
    sentenceList = []
    sentences = sent_tokenize(text)
    for sentence in sentences:
        if sentence not in sentenceList:
            sentenceList.append(sentence.strip())
    return sentenceList


def extract_keywords(text):
    keywordList = []
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = len(text.split())
    custom_kw_extractor = yake.KeywordExtractor(
        lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    keywords = custom_kw_extractor.extract_keywords(text)
    for keyword in keywords:
        if keyword[0] not in keywordList:
            keywordList.append(keyword[0])
    return keywordList


def associate_sentences_keywords(keywords, sentences):
    keyword_processor = KeywordProcessor()
    sentence_keywords = {}

    for word in keywords:
        keyword_processor.add_keyword(word)

    for sentence in sentences:
        sentence_keywords[sentence] = []

    for sentence in sentences:
        keywords_found = keyword_processor.extract_keywords(sentence)
        for key in keywords_found:
            if key not in sentence_keywords[sentence]:
                sentence_keywords[sentence].append(key)

    for key in sentence_keywords.keys():
        values = sentence_keywords[key]
        values = sorted(values, key=len, reverse=True)
        sentence_keywords[key] = values
    return sentence_keywords


def get_T5_Model_Tokenizer():
    question_model = T5ForConditionalGeneration.from_pretrained(
        'ramsrigouthamg/t5_squad_v1')
    question_tokenizer = T5Tokenizer.from_pretrained(
        'ramsrigouthamg/t5_squad_v1')
    T5_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return question_model, question_tokenizer, T5_DEVICE


def get_question(sentence, answer, model, tokenizer, device):
    text = "context: " + sentence + " " + "answer: " + answer  # + " </s>"
    encoding = tokenizer.encode_plus(
        text, max_length=512, padding=True, return_tensors="pt")

    input_ids, attention_mask = encoding["input_ids"].to(
        device), encoding["attention_mask"].to(device)

    model.eval()
    beam_outputs = model.generate(
        input_ids=input_ids, attention_mask=attention_mask,
        max_length=72,
        early_stopping=True,
        num_beams=5,
        num_return_sequences=1
    )

    question = tokenizer.decode(
        beam_outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    question = question.replace("question: ", "")
    return question


def get_distractors_wordnet(word):
    distractors = []
    try:
        syn = wn.synsets(word, 'n')[0]

        word = word.lower()
        orig_word = word
        if len(word.split()) > 0:
            word = word.replace(" ", "_")
        hypernym = syn.hypernyms()
        if len(hypernym) == 0:
            return distractors
        for item in hypernym[0].hyponyms():
            name = item.lemmas()[0].name()
            if name == orig_word:
                continue
            name = name.replace("_", " ")
            name = " ".join(w.capitalize() for w in name.split())
            if name is not None and name not in distractors:
                distractors.append(name)
    except:
        print("Wordnet distractors not found")
    return distractors


def generateQuestion(text, plan):

    # plan 0 = Free
    # plan 1 = Standard
    # plan 2 = Premium

    sentenceList = tokenize_sentences(text)
    keywordList = extract_keywords(text)
    sentence_answer_map = associate_sentences_keywords(
        keywordList, sentenceList)

    T5model, T5tokenizer, T5_DEVICE = get_T5_Model_Tokenizer()
    result = {}
    count = 0
    print("_"*50, '\n')
    for sentence, answer in sentence_answer_map.items():
        if len(answer) != 0:
            distractors = []
            answer = answer[0]  # random.choice(answer)
            question = get_question(
                sentence, answer, T5model, T5tokenizer, T5_DEVICE)

            if plan == "0":
                # Max 100 Char
                print("Free edition")
            elif plan == "1":
                # Unlimited Char
                print("Standard edition")
            elif plan == "2":
                print("Premium edition")
                # With distractors
                pointer = answer
                if len(word_tokenize(pointer)) > 1:
                    distractorsTemp = []
                    pointer = word_tokenize(answer)
                    distractors = get_distractors_wordnet(
                        random.choice(pointer))
                    if len(distractors) != 0:
                        for i, distractor in enumerate(distractors):
                            pointer[0] = distractor
                            distractorsTemp.append(" ".join(pointer))
                            if i == 3:
                                break
                        distractors = distractorsTemp
                else:
                    distractors = get_distractors_wordnet(pointer)

            result[count] = {
                'answer': answer,
                'question': question,
                'distractors': distractors
            }
            print("QUESTION  :", question)
            print("ANSWER    :", answer)
            print("DISTRACTOR:", distractors)
            print("_"*50, '\n')

            count += 1
    return result
