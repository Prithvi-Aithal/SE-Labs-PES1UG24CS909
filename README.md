# Software Engineering Labs (UE24CS341A)

Lab work for the Software Engineering course at PES University. Labs 1 and 3 follow one problem statement through requirements and architecture: **#58, a Digital Art Commission & Watermarking Portal**, where clients post creative briefs, artists upload watermarked work-in-progress drafts, and the final high-resolution files unlock after a milestone payment.

| Lab | Topic | What's inside |
|---|---|---|
| [Lab 1](Lab%201/) | Requirements engineering and UML use-case modelling | Requirements table (5 functional, 2 non-functional, each with acceptance criteria), a use-case diagram with «include» and «extend» relationships, and a use-case flow for "Make Milestone Payment & Unlock Final Asset". See the [Lab 1 README](Lab%201/Lab1_README.md). |
| [Lab 2](Lab%202/) | Agile project tracking in Jira | Deliverable screenshots and a written reflection |
| [Lab 3](Lab%203/) | Architectural pattern selection | A UML component diagram and the case for a microservices architecture (independent scaling of the watermarking pipeline, fault isolation from the payment path) |
| [Lab 4](Lab%204/) | Debugging and extending a Pygame codebase with an AI pair programmer | Fixed an alternating-input deadlock and added AI panic surges, rope-tension and leaning animations, and a match timer with sudden death, with before/after gameplay videos. See the [Lab 4 README](Lab%204/README.md). |

## Running the Lab 4 game

```bash
cd "Lab 4"
pip install pygame        # on Python 3.14+, use pygame-ce instead
python main.py
```

Alternate `A` and `D` to pull the rope, and press `R` to play again from the Game Over screen.
