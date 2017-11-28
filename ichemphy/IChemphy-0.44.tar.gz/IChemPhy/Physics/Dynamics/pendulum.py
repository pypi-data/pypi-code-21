def funcPendulum():
    from matplotlib import animation
    from scipy.integrate import odeint
    from math import pi, cos, sin
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.animation import FuncAnimation

    g = 9.82
    try:
        L = float(input('Enter the length of the Pendlum(m): '))
        m = float(input('Enter the mass of the bob (kg): '))
    except ValueError:
        print('You Entered an invalid input')

    def dx(x, t):
        x1, x2, x3, x4 = x[0], x[1], x[2], x[3]
    
        dx1 = 6.0/(m*L**2) * (2 * x3 - 3 * cos(x1-x2) * x4)/(16 - 9 * cos(x1-x2)**2)
        dx2 = 6.0/(m*L**2) * (8 * x4 - 3 * cos(x1-x2) * x3)/(16 - 9 * cos(x1-x2)**2)
        dx3 = -0.5 * m * L**2 * ( dx1 * dx2 * sin(x1-x2) + 3 * (g/L) * sin(x1))
        dx4 = -0.5 * m * L**2 * (-dx1 * dx2 * sin(x1-x2) + (g/L) * sin(x2))
        return [dx1, dx2, dx3, dx4]

    x0 = [pi/2,pi/2, 0, 0]  # initial state
    t = np.linspace(0, 20, 250) # time coordinates
    x = odeint(dx, x0, t) 
    fig, ax = plt.subplots()
    #pendulum, = plt.plot([], [], 'ro', animated=True)
    pendulum, = plt.plot([], [], linestyle='dashed',marker='o', animated=True)

    def init():
        ax.set_ylim([-1.5, 0.5])
        ax.set_xlim([1, -1])
        pendulum.set_data([], [])
        return pendulum,

    def update(n): 
        # n = frame counter
        # calculate the positions of the pendulums
        x1 = + L * sin(x[n, 0])
        y1 = - L * cos(x[n, 0])
        # update the line data
        pendulum.set_data([0 ,x1], [0 ,y1])
        return pendulum,

    anim = animation.FuncAnimation(fig, update, frames=len(t), init_func=init, blit=True)

    #anim.save('animation.mp4', fps=20)

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
            anim.save(f.name, fps=15, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
            f.flush()
            video = open(f.name, "rb").read()
            f.close()
            anim._encoded_video = base64.b64encode(video).decode('utf-8')
    
        return VIDEO_TAG.format(anim._encoded_video)
    
    from IPython.display import HTML
    def display_animation(anim):
        plt.close(anim._fig)
        return HTML(anim_to_html(anim))
    #display_animation(create_animation(u, theta))

    return display_animation(anim)
