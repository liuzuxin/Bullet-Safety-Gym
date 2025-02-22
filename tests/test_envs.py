"""Check that an environment follows Gym API.

Some functions are from:
https://github.com/hill-a/stable-baselines/blob/master/stable_baselines/common/env_checker.py
"""

import itertools
import unittest
import warnings
from typing import Union

import gymnasium as gym
import numpy as np
from gymnasium import spaces

import bullet_safety_gym.envs  # noqa


def _enforce_array_obs(observation_space: spaces.Space) -> bool:
    """
    Whether to check that the returned observation is a numpy array
    it is not mandatory for `Dict` and `Tuple` spaces.
    """
    return not isinstance(observation_space, (spaces.Dict, spaces.Tuple))


def _check_image_input(observation_space: spaces.Box) -> None:
    """
    Check that the input will be compatible with Stable-Baselines
    when the observation is apparently an image.
    """
    if observation_space.dtype != np.uint8:
        warnings.warn(
            "It seems that your observation is an image but the `dtype` "
            "of your observation_space is not `np.uint8`. "
            "If your observation is not an image, we recommend you to flatten the observation "
            "to have only a 1D vector")

    if np.any(observation_space.low != 0) or np.any(
            observation_space.high != 255):
        warnings.warn(
            "It seems that your observation space is an image but the "
            "upper and lower bounds are not in [0, 255]. "
            "Because the CNN policy normalize automatically the observation "
            "you may encounter issue if the values are not in that range.")

    if observation_space.shape[0] < 36 or observation_space.shape[1] < 36:
        warnings.warn(
            "The minimal resolution for an image is 36x36 for the default CnnPolicy. "
            "You might need to use a custom `cnn_extractor` "
            "cf https://stable-baselines.readthedocs.io/en/master/guide/custom_policy.html"
        )


def _check_unsupported_obs_spaces(env: gym.Env,
                                  observation_space: spaces.Space) -> None:
    """Emit warnings when the observation space used is not supported by Stable-Baselines."""

    if isinstance(observation_space,
                  spaces.Dict) and not isinstance(env, gym.GoalEnv):
        warnings.warn(
            "The observation space is a Dict but the environment is not a gym.GoalEnv "
            "(cf https://github.com/openai/gym/blob/master/gym/core.py), "
            "this is currently not supported by Stable Baselines "
            "(cf https://github.com/hill-a/stable-baselines/issues/133), "
            "you will need to use a custom policy. ")

    if isinstance(observation_space, spaces.Tuple):
        warnings.warn(
            "The observation space is a Tuple,"
            "this is currently not supported by Stable Baselines "
            "(cf https://github.com/hill-a/stable-baselines/issues/133), "
            "you will need to flatten the observation and maybe use a custom policy. "
        )


def _check_obs(obs: Union[tuple, dict, np.ndarray, int],
               observation_space: spaces.Space, method_name: str) -> None:
    """
    Check that the observation returned by the environment
    correspond to the declared one.
    """
    if not isinstance(observation_space, spaces.Tuple):
        assert not isinstance(obs, tuple), (
            "The observation returned by the `{}()` "
            "method should be a single value, not a tuple".format(method_name))

    # The check for a GoalEnv is done by the base class
    if isinstance(observation_space, spaces.Discrete):
        assert isinstance(
            obs, int
        ), "The observation returned by `{}()` method must be an int".format(
            method_name)
    elif _enforce_array_obs(observation_space):
        assert isinstance(
            obs,
            np.ndarray), ("The observation returned by `{}()` "
                          "method must be a numpy array".format(method_name))

    assert observation_space.contains(obs), (
        "The observation returned by the `{}()` "
        "method does not match the given observation space".format(method_name)
    )


def _check_returned_values(env: gym.Env, observation_space: spaces.Space,
                           action_space: spaces.Space) -> None:
    """
    Check the returned values by the env when calling `.reset()` or `.step()` methods.
    """
    # because env inherits from gym.Env, we assume that `reset()` and `step()` methods exists
    obs, info = env.reset()

    _check_obs(obs, observation_space, 'reset')

    # Sample a random action
    action = action_space.sample()
    data = env.step(action)

    assert len(
        data
    ) == 5, "The `step()` method must return four values: obs, reward, terminated, truncated, info"

    # Unpack
    obs, reward, terminated, truncated, info = data

    _check_obs(obs, observation_space, 'step')

    # We also allow int because the reward will be cast to float
    assert isinstance(
        reward,
        (float, int)), "The reward returned by `step()` must be a float"
    assert isinstance(terminated,
                      bool), "The `terminated` signal must be a boolean"
    assert isinstance(
        info,
        dict), "The `info` returned by `step()` must be a python dictionary"

    # if isinstance(env, gym.GoalEnv):
    #     # For a GoalEnv, the keys are checked at reset
    #     assert reward == env.compute_reward(obs['achieved_goal'], obs['desired_goal'],
    #                                         info)


def _check_spaces(env: gym.Env) -> None:
    """
    Check that the observation and action spaces are defined
    and inherit from gym.spaces.Space.
    """
    # Helper to link to the code, because gym has no proper documentation
    gym_spaces = " cf https://github.com/openai/gym/blob/master/gym/spaces/"

    assert hasattr(
        env, 'observation_space'
    ), "You must specify an observation space (cf gym.spaces)" + gym_spaces
    assert hasattr(
        env, 'action_space'
    ), "You must specify an action space (cf gym.spaces)" + gym_spaces

    assert isinstance(
        env.observation_space, spaces.Space
    ), "The observation space must inherit from gym.spaces" + gym_spaces
    assert isinstance(
        env.action_space, spaces.Space
    ), "The action space must inherit from gym.spaces" + gym_spaces


def _check_render(env: gym.Env,
                  warn: bool = True,
                  headless: bool = False) -> None:
    """
    Check the declared render modes and the `render()`/`close()`
    method of the environment.

    :param env: (gym.Env) The environment to check
    :param warn: (bool) Whether to output additional warnings
    :param headless: (bool) Whether to disable render modes
        that require a graphical interface. False by default.
    """
    render_modes = env.metadata.get('render_modes')
    if render_modes is None:
        if warn:
            warnings.warn(
                "No render modes was declared in the environment "
                " (env.metadata['render_modes'] is None or not defined), "
                "you may have trouble when calling `.render()`")

    else:
        # Don't check render mode that require a
        # graphical interface (useful for CI)
        if headless and 'human' in render_modes:
            render_modes.remove('human')
        # Check all declared render modes
        for render_mode in render_modes:
            env.render(mode=render_mode)
        env.close()


def check_env(env: gym.Env,
              warn: bool = True,
              skip_render_check: bool = True) -> None:
    """
    Check that an environment follows Gym API.
    This is particularly useful when using a custom environment.
    Please take a look at https://github.com/openai/gym/blob/master/gym/core.py
    for more information about the API.

    It also optionally check that the environment is compatible with Stable-Baselines.

    :param env: (gym.Env) The Gym environment that will be checked
    :param warn: (bool) Whether to output additional warnings
        mainly related to the interaction with Stable Baselines
    :param skip_render_check: (bool) Whether to skip the checks for the render method.
        True by default (useful for the CI)
    """
    assert isinstance(
        env,
        gym.Env), ("Your environment must inherit from the gym.Env class "
                   "cf https://github.com/openai/gym/blob/master/gym/core.py")

    # ============= Check the spaces (observation and action) ================
    _check_spaces(env)

    # Define aliases for convenience
    observation_space = env.observation_space
    action_space = env.action_space

    # Warn the user if needed.
    # A warning means that the environment may run but not work properly with Stable Baselines algorithms
    if warn:
        _check_unsupported_obs_spaces(env, observation_space)

        # If image, check the low and high values, the type and the number of channels
        # and the shape (minimal value)
        if isinstance(observation_space, spaces.Box) and len(
                observation_space.shape) == 3:
            _check_image_input(observation_space)

        if isinstance(observation_space, spaces.Box) and len(
                observation_space.shape) not in [1, 3]:
            warnings.warn(
                "Your observation has an unconventional shape (neither an image, nor a 1D vector). "
                "We recommend you to flatten the observation "
                "to have only a 1D vector")

        # Check for the action space, it may lead to hard-to-debug issues
        if (isinstance(action_space, spaces.Box) and
            (np.any(np.abs(action_space.low) != np.abs(action_space.high))
             or np.any(np.abs(action_space.low) > 1)
             or np.any(np.abs(action_space.high) > 1))):
            warnings.warn(
                "We recommend you to use a symmetric and normalized Box action space (range=[-1, 1]) "
                "cf https://stable-baselines.readthedocs.io/en/master/guide/rl_tips.html"
            )

    # ============ Check the returned values ===============
    _check_returned_values(env, observation_space, action_space)

    # ==== Check the render method and the declared render modes ====
    if not skip_render_check:
        _check_render(env, warn=warn)

    # The check only works with numpy arrays
    if _enforce_array_obs(observation_space):
        # _check_nan(env)
        pass


class TestEnvs(unittest.TestCase):

    def check_observation_violation(self, x, step):
        """check, if any entry of observations is cut off...,"""
        obs_violated = np.where(np.abs(x) >= 5.0, True, False).any()
        if obs_violated:
            print(f'At step={step} obs={x}')
        self.assertFalse(obs_violated)

    def check_env(self, env_name):
        ''' Run a single environment for a single episode '''
        print(f'Check {env_name}...')
        env = gym.make(env_name)
        x, info = env.reset()
        done, rewards, costs, step = False, 0, 0, 0
        while not done:
            x, r, terminated, truncated, info = env.step(
                env.action_space.sample())
            done = terminated or truncated
            step += 1
            rewards += r
            costs += info.get('cost', 0)
            self.check_observation_violation(x, step)
        print(f'Okay. Steps: {step} Return: {rewards} Cost: {costs}')
        env.close()

    def test_all_envs(self):
        """ Run all the benchmark environments."""
        checked_envs = []
        agent_list = ['Ball', 'Car', 'Ant', 'Drone']
        task_list = ['Reach', 'Circle', 'Run', 'Gather']

        for (agent, task) in itertools.product(agent_list, task_list):
            env_name = str(f'Safety{agent}{task}-v0')
            self.check_env(env_name)
            checked_envs.append(env_name)

        # now test all Envs which have been registered but were not covered
        # by previous loop
        for env_spec in gym.envs.registry.values():
            if 'Safety' in env_spec.id and env_spec.id not in checked_envs:
                self.check_env(env_spec.id)

    def test_gym_api(self):
        """Check that an environment follows Gym API."""
        for env_spec in gym.envs.registry.values():
            if 'Safety' in env_spec.id:
                env = gym.make(env_spec.id)
                check_env(env)


if __name__ == '__main__':
    unittest.main()
