import gym
env = gym.make('CartPole-v0')
env.reset()
done = False
for t in range(1000):
    env.render()
    observation, reward, done, info = env.step(
        env.action_space.sample())  # take a random action

    if done:
        print("Episode finished after {} timesteps".format(t+1))
        break
env.close()
