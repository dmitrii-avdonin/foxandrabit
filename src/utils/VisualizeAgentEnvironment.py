import matplotlib.pyplot as plt
import numpy as np

plt.show(block = False)

def visualizeAgentEnvironment(data):
    #Create coordinates
    plt.clf()
    plt.axes().set_aspect('equal')    
    x_coords = []
    y_coords = []
    step=0.5
    for row in range(len(data)):
        for col in range(len(data[row])):
            x_coords = np.append(x_coords,col+step)
            y_coords = np.append(y_coords,row+step)
        

    #Grass
    colors = [[0.,0.,0.]]
    area = (30 * 1.5)**2  # 0 to 15 point radii
    for row in reversed(range(len(data))):
        for col in range(len(data[row])):
            amount_of_grass = data[row][col][0]
            color = [0.915,0.915,0.915]
            if amount_of_grass>0.:
                color = [0.9-amount_of_grass,0.8,0.9-amount_of_grass]
            colors = np.vstack([colors,color])
                
    colors = np.delete(colors, 0, 0)

    plt.scatter(x_coords, y_coords, s=area, marker='s', c=colors, alpha=1)
    plt.xticks(np.arange(0, len(data[0])+1, 1.0))
    plt.yticks(np.arange(0, len(data[0])+1, 1.0))



    #Agents
    colors = [[0.,0.,0.,0.]]
    area = (30 * 0.5)**2  # 0 to 15 point radii
    k=0
    for row in reversed(range(len(data))):
        for col in range(len(data[row])):
            agent = data[row][col][1]
            fullness = data[row][col][2]
            current_color = [1.,1.,1.,0.] #no agent
            if agent==1: #fox
                current_color = [1.,0.,0.,1.]
            if agent==1 or agent==2:
                plt.gca().annotate(str(fullness),
                                xy=(x_coords[k]+0.1,y_coords[k]+0.2), xycoords='data')
            if agent==2: #rabbit
                current_color = [0.,0.,1.,1.]
                
            colors = np.vstack([colors,current_color])
            k+=1
                
    colors = np.delete(colors, 0, 0)

    plt.scatter(x_coords, y_coords, s=area, marker='s', c=colors)
    plt.xticks(np.arange(0, len(data[0])+1, 1.0))
    plt.yticks(np.arange(0, len(data[0])+1, 1.0))



    plt.show(block = False)
    plt.pause(0.001)

if __name__ == "__main__":
    data  = [[[0.1,0.,5. ],[0.9,0.,5.],[0.,2.,5.],[0.6,0.,5.],[0.9,0.,5.]],
           [[0.2,0.,5. ],[0.7,0.,5.],[0.,0.,5.],[0. ,0.,5.],[0.9,0.,5.]],
           [[0.7,1.,5. ],[0. ,0.,5.],[0.,2.,5.],[0.3,0.,5.],[0. ,1.,5.]],
           [[0.9,1.,5. ],[0.5,1.,5.],[0.,0.,5.],[0.4,0.,5.],[0.2,0.,5.]],
           [[0.9,0.,5. ],[0.8,0.,5.],[0.,0.,5.],[0.9,0.,5.],[0.5,0.,5.]]]
    visualizeAgentEnvironment(data)