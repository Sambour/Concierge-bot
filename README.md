# Concierge-bot

## Description

This repo is for the project [*Automated Interactive Domain-Specific Conversational Agents that Understand Human Dialogs*](https://arxiv.org/abs/2303.08941).

We constructed an AutoConcierge for recommending local restaurants around UT Dallas by the preferences of the users.

It serves people by asking people questions of their preferences, and the users are also allowed to propose their own requirements. After collecting enough information, AutoConcierge will recommend the best matched restaurants for the user.

## Requirement

- s(CASP) query-driven ASP solver:
available at [s(CASP) GitLab page](https://gitlab.software.imdea.org/ciao-lang/sCASP).

- OpenAI Python package with secret key in environmental path:
The Python package can be installed by `pip install openai`

## How To Run

1. Clone this repo.
2. (optional) Prepare your own knowledge base follow the format of `data/knowledge.pl` and cover it.
3. Run `python main.py` and start chat.

