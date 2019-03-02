# TODO: main program body looping -- exit when an exit state is reached
# TODO: add score and ASCII arcade start screen
# TODO: look up module and package organization
# TODO: look up if basename imports like these first ones chuck everything
import csv
import os
import random

from contextlib import ExitStack
from enum import Enum, unique
from itertools import zip_longest
from pick import pick


class Question(object):
    # TODO: look up how to document attribute information
    # TODO: make attributes self-documenting
    # TODO: where to force expectation, caller or handler
    def __init__(self, question, choices, answer, difficulty, chosen=None):
        # question = also known as the stem
        self.question = question
        self.choices = choices
        # answer = also known as a keyed option
        self.answer = answer
        self.difficulty = difficulty
        # rename this to answer
        self.chosen = chosen
    
    def __repr__(self):
        return "{cls}({question}, {chosen}, {answer})".format(
                                cls=self.__class__.__name__,
                                question=self.question,
                                answer=self.answer,
                                chosen=self.chosen)
    
    def prompt(self):
        return f'{self.question} [{self.difficulty.name}]'

@unique
class Difficulty(Enum):
    __order__ = "EASY MEDIUM HARD"
    EASY = 1
    MEDIUM = 2
    HARD = 3

CATEGORIES = {'Mathematics':'math', 'Science':'science', 
              'Philippine History':'ph'}
NUM_QUESTIONS = 10


def choose_category():
    """Returns the value of the chosen category as a string."""
    main_prompt = 'Please choose your desired quiz category:'
    categories = list(CATEGORIES.keys())
    chosen = _pick(prompt=main_prompt, options=categories)
    return CATEGORIES[chosen]

def start_quiz():
    """Returns a list of answered Question objects."""
    category = choose_category()
    questions = generate_questions(category)
    # Answering part
    for question in questions:
        chosen = _pick(prompt=question.prompt(), options=question.choices)
        question.chosen = chosen
    return questions

def grade_quiz(answered_questions):
    """Returns the score given a list of answered Question objects."""
    return sum(1 * question.difficulty.value 
               for question in answered_questions 
               if question.answer == question.chosen)

def get_total(answered_questions):
    return sum(1 * question.difficulty.value
               for question in answered_questions)

def generate_questions(category):
    # category = dirname of the chosen topic
    """Returns a randomized list of Question objects from the given category."""
    questions = []
    filenames_by_difficulty = dict()
    # {<Difficulty.EASY: 1>:<easy_filenames>, 
    #  <Difficulty.MEDIUM: 2>:<medium_filenames} ... }
    category_dir = os.path.abspath(category)
    for d in Difficulty:
        filenames_by_difficulty[d] = [os.path.join(category_dir, f) 
                                      for f in os.listdir(category_dir)
                                      if d.name.lower() in f]

    with ExitStack() as stack:
        for difficulty, fnames in filenames_by_difficulty.items():
            files = [stack.enter_context(open(fname)) for fname in fnames]
            # opens in this order -> answers, choices, questions
            # change the file handle to a csv reader object
            files[1]  = csv.reader(files[1])
            for answer, choices, question in zip_longest(*files):
                answer = answer.strip()
                question = question.strip()
                questions.append(Question(question=question,
                                        choices=choices,
                                        answer=answer,
                                        difficulty=difficulty))
    random.shuffle(questions)
    return questions[:NUM_QUESTIONS]

def _pick(prompt, options, indicator='=>'):
    # TODO: look up proper method documentation
    # TODO: look up what happens when you do this parameter->argument naming confusion
    """
    
    A modified interface for pick.pick.
    Side effect: displays to the console with a curses-based interactive selection list.

    Parameters:
    option : a list of options
    """
    option, _ = pick(options=options, title=prompt, indicator=indicator)
    return option


if __name__ == "__main__":
    answered_questions = start_quiz()
    score = grade_quiz(answered_questions)
    total = get_total(answered_questions)
    print(f"score: {score}")
    print(f"total: {total}")
    print(f"percentage: {(score / total) * 100}%")