import numpy as np
from nose2 import tools
import os

import logging
logger = logging.getLogger(__name__)

import gym
from gym import envs

specs = [spec for spec in envs.registry.all() if spec._entry_point is not None]
@tools.params(*specs)
def test_env(spec):
    # Skip mujoco tests for pull request CI
    skip_mujoco = not (os.environ.get('MUJOCO_KEY_BUNDLE') or os.path.exists(os.path.expanduser('~/.mujoco')))
    if skip_mujoco and spec._entry_point.startswith('gym.envs.mujoco:'):
        return

    # TODO(jonas 2016-05-11): Re-enable these tests after fixing box2d-py
    if spec._entry_point.startswith('gym.envs.box2d:'):
        logger.warn("Skipping tests for box2d env {}".format(spec._entry_point))
        return

    env1 = spec.make()
    env1.seed(0)
    action_samples1 = [env1.action_space.sample() for i in range(4)]
    observation_samples1 = [env1.observation_space.sample() for i in range(4)]
    initial_observation1 = env1.reset()
    step_responses1 = [env1.step(action) for action in action_samples1]
    env1.close()

    env2 = spec.make()
    env2.seed(0)
    action_samples2 = [env2.action_space.sample() for i in range(4)]
    observation_samples2 = [env2.observation_space.sample() for i in range(4)]
    initial_observation2 = env2.reset()
    step_responses2 = [env2.step(action) for action in action_samples2]
    env2.close()

    for i, (action_sample1, action_sample2) in enumerate(zip(action_samples1, action_samples2)):
        assert np.array_equal(action_sample1, action_sample2), '[{}] action_sample1: {}, action_sample2: {}'.format(i, action_sample1, action_sample2)

    for i, (observation_sample1, observation_sample2) in enumerate(zip(observation_samples1, observation_samples2)):
        # Allows for NaNs
        np.testing.assert_array_equal(observation_sample1, observation_sample2)

    # Don't check rollout equality if it's a a nondeterministic
    # environment.
    if spec.nondeterministic:
        return

    assert np.array_equal(initial_observation1, initial_observation2), 'initial_observation1: {}, initial_observation2: {}'.format(initial_observation1, initial_observation2)

    for i, ((o1, r1, d1, i1), (o2, r2, d2, i2)) in enumerate(zip(step_responses1, step_responses2)):
        assert_equals(o1, o2, '[{}] '.format(i))
        assert r1 == r2, '[{}] r1: {}, r2: {}'.format(i, r1, r2)
        assert d1 == d2, '[{}] d1: {}, d2: {}'.format(i, d1, d2)

        # Go returns a Pachi game board in info, which doesn't
        # properly check equality. For now, we hack around this by
        # just skipping Go.
        if spec.id not in ['Go9x9-v0', 'Go19x19-v0']:
            assert_equals(i1, i2, '[{}] '.format(i))

def assert_equals(a, b, prefix=None):
    assert type(a) == type(b), "{}Differing types: {} and {}".format(prefix, a, b)
    if isinstance(a, dict):
        assert list(a.keys()) == list(b.keys()), "{}Key sets differ: {} and {}".format(prefix, a, b)

        for k in a.keys():
            v_a = a[k]
            v_b = b[k]
            assert_equals(v_a, v_b)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    else:
        assert a == b
