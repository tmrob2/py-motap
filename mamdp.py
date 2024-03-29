"""
This script will consist of constructing a MAMDP model
"""
import rust_motap
from rust_motap import mamdp as mamdplib

NUM_TASKS = 6
NUM_AGENTS = 2

# define a set of global action

agent = rust_motap.Agent(0, list(range(5)), [1, 2])
# for this experiment we just want some identical copies of the agents
# define agent transitions
agent.add_transition(0, 0, [(0, 0.01, ""), (1, 0.99, "init")])
agent.add_transition(1, 0, [(2, 1., "ready")])
agent.add_transition(2, 0, [(3, 0.99, "send"), (4, 0.01, "exit")])
agent.add_transition(2, 1, [(4, 1.0, "exit")])
agent.add_transition(3, 0, [(2, 1.0, "ready")])
agent.add_transition(4, 0, [(0, 1.0, "")])
# define rewards
agent.add_reward(0, 0, -1)
agent.add_reward(1, 0, -1)
agent.add_reward(2, 0, -1)
agent.add_reward(2, 1, -1)
agent.add_reward(3, 0, -1)
agent.add_reward(4, 0, -1)

# Specify the agents
team = rust_motap.Team()
for i in range(0, NUM_AGENTS):
    team.add_agent(agent.clone())


def construct_message_sending_task(r):
    task = rust_motap.DFA(list(range(0, 6)), 0, [2 + r + 1], [2 + r + 3], [2 + r + 2])
    for w in ["", "send", "ready", "exit"]:
        task.add_transition(0, w, 1)
    task.add_transition(0, "init", 2)
    task.add_transition(1, "init", 2)
    for w in ["", "send", "ready", "exit"]:
        task.add_transition(1, w, 1)
    for repeat in range(0, r + 1):
        task.add_transition(2 + repeat, "", 2 + repeat)
        task.add_transition(2 + repeat, "init", 2 + repeat)
        task.add_transition(2 + repeat, "ready", 2 + repeat)
        task.add_transition(2 + repeat, "send", 2 + repeat + 1)
        task.add_transition(2 + repeat, "exit", 2 + r + 3)
    for w in ["", "send", "ready", "exit", "init"]:
        task.add_transition(2 + r + 1, w, 2 + r + 2)
        task.add_transition(2 + r + 2, w, 2 + r + 2)
        task.add_transition(2 + r + 3, w, 2 + r + 3)
    return task

# mission is a python owned object which is a collection of tasks, tasks are DFAs
mission = rust_motap.Mission()
for k in range(0, NUM_TASKS):
    mission.add_task(construct_message_sending_task(k))

# do some operation to check that this mission is being constructed correctly. 
mission.print_task_transitions()
team.print_initial_states()


if __name__ == "__main__":
    # start by determining the initial transitions of the state
    # define agent 1
    initial_state = mamdplib.construct_initial_state(mission, team)
    print("Initial state: ", initial_state)
    #rust_motap.find_neighbour_states(
    #    initial_state, [0] * NUM_AGENTS, team, mission, NUM_AGENTS, NUM_TASKS
    #)
    # action_products = rust_motap.compute_input_actions(initial_state, team, mission, NUM_AGENTS, NUM_TASKS)
    # Run a test over some transitions
    #rust_motap.test_get_all_transitions(initial_state, team, mission, NUM_AGENTS, NUM_TASKS);
    # Test a new state
    # let the state be one of the transition states from the initial state 
    # following a task allocation
    #test_state = [0, 1, 1, 2, 0, 0, 1]
    #rust_motap.test_get_all_transitions(test_state, team, mission, NUM_AGENTS, NUM_TASKS)
    
    # Build the MAMDP model
    mamdp = mamdplib.build_model(initial_state, team, mission, NUM_AGENTS, NUM_TASKS)
    
    # If the following is true, then the MAMDP has a state in which all tasks
    # are completed reachable from the initial state. 

    # MAMDP model size
    print("|P|, ", mamdp.get_number_states())
    mamdp.print_model_attr()
    #mamdp.print_state_mapping()
    print(mamdp.states[70])
    mamdp.print_state_test(70)
    #mamdp.print_transitions()
    #mamdp.print_rewards()
    #mamdp.find_initial_transitions()
    assert mamdplib.assert_done(mamdp, mission, NUM_AGENTS, NUM_TASKS) is True
    # convert to a condensed MDP
    #mamdp.print_action_mapping()
    momdp = mamdplib.convert_to_multobj_mdp(mamdp, team, mission, NUM_AGENTS, NUM_TASKS)
    #momdp.print_transitions()
    ##momdp.print_available_actions()
    target = [-30.] * NUM_AGENTS + [0.9] * NUM_TASKS
    eps = 1e-5
    (mu, r) = rust_motap.multiobjective_scheduler_synthesis(
        eps, target, momdp, NUM_AGENTS, NUM_TASKS
    )
    momdp.print_model_size()
    