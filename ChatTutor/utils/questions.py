import nice_functions as nf
from utils.get_char import get_char
from typing import List


def multiple_options_only_text(options_list: List[str]) -> str: 
    text_list = []
    for option in options_list:
        _tmp = option.split(",")
        if len(_tmp) < 3:
            raise (
                _tmp,
                " is not a valid option. Options should be defined as 'colour,letter,text'",
            )
        letter = _tmp[1].strip()
        if letter == "":
            letter = "<enter>"
        letter_color = eval("nf.bold(nf." + _tmp[0].strip() + "(letter))")
        text = ",".join(_tmp[2:]).strip()
        text_list.append(f" {letter_color} - {text}")
    return "\n".join(text_list)


def multiple_options(
    question: str,
    options_list: List[str]=[],
    input_text: str="Type your answer and press enter: ",
    multiple_letters: bool=False,
    answer: str=None,
) -> str:
    if question:
        print(question)
    if options_list:
        text = multiple_options_only_text(options_list)
        print(text)
    if answer:
        print(rf"---- > your answer was {nf.yellow(answer)} <-----")
        return answer
    if not multiple_letters:
        return get_char()
    else:
        return input(input_text)


def yes_no_question(question: str, enter: str="yes") -> bool:
    print(question, end="")
    if enter == "yes":
        print(
            f" [{nf.bold(nf.red('n'))}o/{nf.bold(nf.green('y'))}es ({nf.bold(nf.green('enter'))})]:"
        )
    elif enter == "no":
        print(
            f"[{nf.bold(nf.red('n'))}o ({nf.bold(nf.red('enter'))})/{nf.bold(nf.green('y'))}es]:"
        )
    else:
        print(f"[{nf.bold(nf.red('n'))}o/{nf.bold(nf.green('y'))}es]:")
    while True:
        r = get_char()
        if r == "y":
            return True
        if r == "n":
            return False
        if r == "\r" and enter == "yes":
            return True
        if r == "\r" and enter == "no":
            return False


def no_changes() -> None:
    print(f"No changes {nf.ok_symbol}")


def no_changes_press_enter() -> None:
    print(f"No changes {nf.ok_symbol}")
    input("Press enter to continue")


def press_enter(message: str="") -> None:
    if message:
        message = f"{message}. "
    input(f"{message}Press enter to continue")


def done_press_enter(message: str="Done") -> None:
    input(f"{message} {nf.ok_symbol}\nPress enter to continue")


def done(message: str="Done") -> None:
    print(f"{message} {nf.ok_symbol}")


def failed(message: str="Failed") -> None:
    print(f"{message} {nf.fail_symbol}")


def failed_press_enter(message: str="Failed") -> None:
    input(f"{message} {nf.fail_symbol}\nPress enter to continue")


def processing_answer() -> None:
    print("Processing answer...")
