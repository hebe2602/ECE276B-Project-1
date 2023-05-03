from utils import *
from example import example_use_of_gym_env
from minigrid.core.world_object import Wall, Goal
from operator import add
import copy

MF = 0  # Move Forward
TL = 1  # Turn Left
TR = 2  # Turn Right
PK = 3  # Pickup Key
UD = 4  # Unlock 



def state_space_init(env,info):
    w = env.width
    h = env.height
    goal_loc = info['goal_pos']
    orientation = [[1,0],[0,1],[-1,0],[0,-1]] #Right,down,left,up
    state_space_list = []
    green_square_location_ind = []
    start_ind = 0


    key_door_info = [{'open': [0, 0], 'key': 0},
                     {'open': [0, 0], 'key': 1},
                     {'open': [1, 0], 'key': 0},
                     {'open': [1, 0], 'key': 1},
                     {'open': [0, 1], 'key': 0},
                     {'open': [0, 1], 'key': 1},
                     {'open': [1, 1], 'key': 0},
                     {'open': [1, 1], 'key': 1}]
    key_door_info_size = len(key_door_info)
    
    start_pos_agent = [info['init_agent_pos'][0],info['init_agent_pos'][1]]

    
    for w_i in range(w):
        for h_i in range(h):
            for o in orientation:
                for j in range(key_door_info_size):
                    state_i = {}
                    state_i['agent_pos'] = [w_i,h_i]
                    state_i['agent_or'] = o
                    state_i['have_key'] = key_door_info[j]['key']
                    state_i['door'] = key_door_info[j]['open']
                    index = len(state_space_list)
                    state_i['ind'] = index


                    if not isinstance(env.grid.get(w_i,h_i), Wall):
                        state_space_list.append(state_i)

                    if w_i == goal_loc[0] and h_i == goal_loc[1]:
                        green_square_location_ind.append(index-1)

                    
                    if state_i['agent_pos'] == start_pos_agent and (state_i['agent_or'] == info['init_agent_dir']).all():
                        if state_i['door'] == info['door_open'] and state_i['have_key'] == 0:
                            start_ind = index-1

                   
                    
    return state_space_list, green_square_location_ind,start_ind



def next_action(a,b,key_pos,door_pos):
    possible_actions = [MF, TL, TR, PK, UD]
    for action in possible_actions:
        if action == UD:
            if ([pos + ori for pos, ori in zip(a['agent_pos'], a['agent_or'])] == door_pos[0]).all() or ([pos + ori for pos, ori in zip(a['agent_pos'], a['agent_or'])] == door_pos[1]).all(): #check both doors
                if a['agent_pos'] == b['agent_pos'] and a['agent_or'] == b['agent_or']:
                    if a['have_key'] == 1:
                        if  a['door'] != b['door'] and a['have_key'] == b['have_key']: #door locked between the states
                            return UD
        if action == PK:
            if ([pos + ori for pos, ori in zip(a['agent_pos'], a['agent_or'])] == key_pos).all():
                if a['agent_pos'] == b['agent_pos'] and a['agent_or'] == b['agent_or']:
                    if a['have_key'] != b['have_key'] and a['door'] == b['door']: #no key in next state and doors locked 
                        return PK
        if action == TR:
            if a['agent_pos'] == b['agent_pos'] and a['have_key'] == b['have_key'] and a['door'] == b['door']:
                arr = np.array([[0,-1],[1,0]])
                next_or = np.dot(arr,np.array((a['agent_or'])))
                if (b['agent_or'] == next_or).all():
                    return TR
                
        if action == TL:
            if a['agent_pos'] == b['agent_pos'] and a['have_key'] == b['have_key'] and a['door'] == b['door']:
                arr = np.array([[0,1],[-1,0]])
                next_or = np.dot(arr,np.array((a['agent_or'])))
                if (b['agent_or'] == next_or).all():
                    return TL
                
        if action == MF:
            if a['agent_or'] == b['agent_or'] and [pos + ori for pos, ori in zip(a['agent_pos'], a['agent_or'])] == b['agent_pos']:
                if a['have_key'] == b['have_key'] and a['door'] == b['door']:
                    #dont move forward if door is locked:
                    if (b['agent_pos'] == door_pos[0]).all() and b['door'] == 0:
                        return 5
                    if (b['agent_pos'] == door_pos[1]).all() and b['door'] == 0:
                        return 5
                    return MF
    return 5

def Q_matrix(state_space,info):
    key_pos = info['key_pos']
    door_pos = info['door_pos']
    Q = np.zeros((len(state_space),len(state_space)))
    for i in range(len(state_space)):
        for j in range(len(state_space)):
            if i == j: #same state
                Q[i,j] = 0
            else:
                action = next_action(state_space[i],state_space[j],key_pos,door_pos)
                if action == 5:
                    Q[i,j] = np.inf
                else:
                    Q[i,j] = action
    return Q

def doorkey_problem(env,info):
    env = copy.deepcopy(env)
    state_space,green_square_index,start_index = state_space_init(env,info)
    Q = Q_matrix(state_space,info)

    #Label Correcting Algorithm from slide 14 lecture 5
    T = len(state_space)

    parent_list = [0]*T
    #g = np.inf*np.ones(T)
    #g = float('inf')*np.ones(T)
    g = np.full(T,float('inf'))
    g[start_index] = 0
    open_list = [state_space[start_index]]
    while len(open_list) > 0:
        i = open_list.pop(0) #BFS variation
        

        #initialize children
        children_list = []
        c = Q[i['ind']]
        for c_i in range(len(c)):
            if c[c_i] != 5 and c[c_i] != np.inf: #add reachable states to children
                children_list.append(state_space[c_i])
        for j in children_list:
            min_val, min_index = min((val,ind) for ind,val in enumerate(g[green_square_index]))
            
            
        
            temp_green_square_index = green_square_index[min_index]
            c = 1
        
            if ((g[i['ind']]) + c) < g[j['ind']] and ((g[i['ind']]) + c) < g[temp_green_square_index]:
                g[j['ind']] = ((g[i['ind']]) + c)
                parent_list[j['ind']] = i
                if j['ind'] != temp_green_square_index:
                    open_list.append(state_space[j['ind']])

    ###########

    #Finding optimal trajectory from the results of the Label correction algorithm
    optimal_path, optimal_ind = min((val,ind) for ind,val in enumerate(g[green_square_index]))
    next_state = state_space[green_square_index[optimal_ind]]

    optim_act_seq = []
    for i in range(int(optimal_path)):
        prev_state = parent_list[next_state['ind']]
        next_action = Q[prev_state['ind'],next_state['ind']]
        optim_act_seq.insert(0, next_action)
        next_state = prev_state

    for action in optim_act_seq:
        _, done = step(env, action)

    if done:
        print("Green Square reached")

    print("Step Count to Green Square: {}".format(env.step_count))
    return optim_act_seq


def partB():
    env_folder = "./envs/random_envs"
    env, info, env_path = load_random_env(env_folder)
    print("env, ", env)
    plot_env(env)
    print("info ",  info)
    print("env_path,", env_path)

    seq = doorkey_problem(env, info)  # find the optimal action sequence
    #draw_gif_from_seq(seq, load_env(env_path))  # draw a GIF & save
    return seq


if __name__ == "__main__":
    seq = partB()
    print("optimal Action Sequence: ", seq )













    


