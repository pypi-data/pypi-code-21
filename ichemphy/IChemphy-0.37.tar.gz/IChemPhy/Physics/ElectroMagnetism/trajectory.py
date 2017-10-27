def funcElectroMagneticTrajectory():
    import numpy as np
    from scipy.integrate import ode, odeint
    
    B=list()
    V0=list()
    E=list()
    A0=list()

    try:
        print("Enter the Magnetic Field :") 
        for i in range(int(3)):
            n=input("B"+str(i+1)+" :")
            B.append(int(n))
        
        print("Enter the Velocity :") 
        for i in range(int(3)):
            n=input("V"+str(i+1)+" :")
            V0.append(int(n))

        print("Enter the positions :") 
        for i in range(int(3)):
            n=input("A"+str(i+1)+" :")
            A0.append(int(n))

        print("Enter the Electric field :") 
        for i in range(int(3)):
            n=input("E"+str(i+1)+" :")
            E.append(int(n))
                                                     
        '''V0 = float(input('Enter the initial velocity(in the form of [ , , ]): '))
        A0 = float(input('Enter the initial position of the charge(in the form of [ , , ]): '))
        E = float(input('Enter the Electric Field(in the form of [ , , ]): ')) '''

        m = float(input('Enter the mass of the charged particle(in kg): '))
        q = float(input('Enter the magnitude of the charge on the particle(in C): '))  
    except ValueError:
        print('You Entered an invalid input')
    '''B=[0,2,0]
    V0=[4,5,6]
    A0=[1,2,3]
    E=[4,5,6]
    m=0.01
    q=6'''

    def f(y,t):
        VB=np.cross(B, [y[0], y[1], y[2]])
        x= [0,0,0,0,0,0]
        x[0]=(q/m)*(E[0]+VB[0])
        x[1] = (q / m) * (E[1] + VB[1])
        x[2] = (q / m) * (E[2] + VB[2])
        x[3]=y[3]
        x[4]=y[4]
        x[5]=y[5]
        return x
    
    t = np.linspace(0.0001, 10, 1000)
    x0 = np.array([0, 0, 0])
    v0 = np.array([1, 1, 0])
    initial_conditions = np.concatenate((x0, v0))
    yvals = odeint(f,initial_conditions,t)
    positions= yvals[:, :3]
    #%matplotlib inline
    import matplotlib.pyplot as plt
    plt.plot(positions[:, 1], positions[:, 2])

    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot3D(positions[:, 0], positions[:, 1], positions[:, 2])

    B1 = np.array([x0[0], x0[1], -1])
    B2 = np.array([60, 0, 0])
    B_axis = np.vstack((B1, B1 + B2))
    ax.plot3D(B_axis[:, 0], 
             B_axis[:, 1],
             B_axis[:, 2])
    plt.xlabel('x')
    plt.ylabel('y')
    ax.set_zlabel('z')
    ax.text3D((B1 + B2)[0], (B1 + B2)[1], (B1 + B2)[2], "B field")

    from tempfile import NamedTemporaryFile
    import base64 
    from matplotlib import animation
    VIDEO_TAG = """<video controls>
     <source src="data:video/x-m4v;base64,{0}" type="video/mp4">
     Your browser does not support the video tag.
    </video>"""

    def anim_to_html(anim):
        if not hasattr(anim, '_encoded_video'):
            f = NamedTemporaryFile(suffix='.mp4', delete=False)
            anim.save(f.name, fps=20, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
            f.flush()
            video = open(f.name, "rb").read()
            f.close()
            anim._encoded_video = base64.b64encode(video).decode('utf-8')
    
        return VIDEO_TAG.format(anim._encoded_video)
    
    from IPython.display import HTML

    def display_animation(anim):
        plt.close(anim._fig)
        return HTML(anim_to_html(anim))
    
    FRAMES = 50
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    def init():
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
    
    # animation function.  This is called sequentially
    def animate(i):
        current_index = int(positions.shape[0] / FRAMES * i)
        ax.cla()
        ax.plot3D(positions[:current_index, 0], 
                  positions[:current_index, 1], 
                  positions[:current_index, 2])
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
    # call the animator.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=FRAMES, interval=100)

    # call our new function to display the animation
    return display_animation(anim)
