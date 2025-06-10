# Logbook

## 27/05/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Initial discussion regarding first steps for the project. It was determined that after some precursory literature review regarding ACO (ant colony optimisation), I would begin to implement an ACO python package and begin to apply it to the [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem), with the idea being to use this package to solve another problem (such as feature selection) later on.
    - Github repo health was discussed, as well as making sure I familiarise myself with the academic integrity expectations of the IRP.
    - The project plan was also mentioned, and that I should start considering what I might want to include in it.
- **Feedback received**
    - The initial plan was well received, and Marijan suggested meeting a minimum of once every two weeks (ideally once a week) to ensure that I stay on course.
- **Plan before next meeting**:
    - Read existing papers on ACO and start building a bibliography.
    - Try to get a local latex install running (overleaf can be used as a backup if this does not work).
    - At least get some initial ant simulation running, even if it not perfect.

## 04/06/2025
- **Present**: Benjamin Gorrie (joined online), Marijan Beg
- **Key points discussed**
    - Showing Marijan progress done so far, namely the first implementation of the Ant System. Marijan happy with current results, although some basic visualisations need to be implemented. The ants are within 0.5% of the best path of the [Oliver30 nodes](https://stevedower.id.au/research/oliver-30).
    - It was suggested that I slightly change the structure of the repo by moving items in `aco/` one level up. 
    - The main point raised in the meeting was that I should think of an application that uses this Ant System (or some variant of it). This application should be genuinely interesting to me so as not to lose my interest over the course of the project. The initially suggested feature selection idea is probably going to be difficult to implement. Marijan raised the possiblity of using the aco package to solve a scheduling problem or aid the job distribution system that is currently in use in the imperial HPC. This is the main thing I want to have an idea of before next meeting.
- **Feedback received**
    - The current implementation was well received, although it will probably be more clear what is actually going on once some visualisations are produced.
- **Plan before next meeting**
    - Code some basic visualisation functions.
    - Change the directory structure as requested.
    - Think of an interesting and potential novel applications of the Ant System.

## 10/06/2025
- **Present**: Benjamin Gorrie, Marijan Beg
- **Key points discussed**
    - Showed Marijan current basic visualisations. The path one in particular is helpful to determine what the ants end up doing.
    - The main topic discussed was the direction that the project is going to take moving forward, i.e. what should this Ant System be applied to?
    - I suggested a dynamic job-shop scheduling problem (DJSP) that can be solved by the ants. The example I gave was in a hospital, where surgeries overrun/there are emergency arrivals/some machines stop working. In this context, is it possible to reschedule the doctor's existing schedule while causing as minimal a disruption as possible? Is it possible to do this quickly without rescheduling everything from scratch (leveraging the pheromone trails left behind by the ants)? Marijan liked this idea, and stressed that while the context is good for motivating the problem, the package should be as application-agnostic as possible.
    - The project plan deadline was also brought up.
- **Feedback received**
    - DJSP seems to be a good direction to take.
- **Plan before next meeting**
    - Finish the project plan before the deadline.
    - Once this is done, start working on a scheduler using ants. Start with a static scheduler for now, and then try to make it dynamic later.
