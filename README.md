# What does impact mean?

Engineering impact in our definition will be defined by 3 clear aspects,
such that we can avoid any hand-waving weird metrics.

1. Merged PRs 
2. Meaningful merged PRs 
3. Reviews given

Each of these aspects is provided a score, we can vary this, but to start:

## Weights
- Merged PRs: 35% 
- Meaningful Merged PRs: 45%
- Reviews given: 20%

The reason I've chosen these is because, engineers who consistently ship work that is substantial
and help others ship through code review in my experience have been some of the best to work with.

### How do we define Meaningful Merged PRs
- This is essentially based on a depth heuristic, we'll look at three areas for this:
1. changed files 
2. top level areas touched 
3. review count

Each will have a threshold that will add to the weighting

## Supporting Evidence
The key pillars for supporting evidence required for our dashboard are
- representative PRs 
    - We want to know where the evidence links back to 
- Unique areas touched 
    - The more systems that a PR spans requires a deeper working knowledge, it's hard to build
    things that work outside of a singular subsystem
- Unique authors reviewed
    - The more people working on something usually correlates with the amount of impact it may have/
    how important it is.

- Median time to merge
    - If possible we can look at how long PRs are taking to be merged,
    this can go both ways, if someone's PRs are merged fast consistently,
    this means that they might be adding a ton of value, but they 
    could also be working on simpler things.


### Other data we will derive:
- Merged Pr count per engineer
- Meaningful merged PR count per engineer
- reviews given per engineer 
- unique areas touched per engineer
- unique authors reviewed per engineer 
- median time to merge per engineer

# Information required from GitHub
- PR Numbers
- PR title
- PR URL
- author login
- author avatar
- created_at
- merged_at
- merged boolean
- changed files count
- reviews for each PR:
    - reviewer login
    - review state
    - submitted_at

### Data handling

#### Normalization
- We want to normalize all metrics when we are performing scoring
- For display we will showcase raw metrics

# How do we display this information:
## Stack:
- React
- TypeScript
- Custom CSS
- Recharts (For plotting the metrics)











