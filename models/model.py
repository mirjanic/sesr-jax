import jax.numpy as jnp
import haiku as hk

import models.sesr as sesr
import models.sesr_collapsed as sesr_c
from models.collapser import collapse


def get_sesr_args(name: str):
    return {
        'M3':  {'m': 3,  'f': 16, 'hidden_dim': 256},
        'M5':  {'m': 5,  'f': 16, 'hidden_dim': 256},
        'M11': {'m': 11, 'f': 16, 'hidden_dim': 256},  # TODO or f=32?
        }.get(name)


class Model:

    def expanded_fn(self, images: jnp.ndarray, **kwargs) -> jnp.ndarray:
        net = self.expanded(**kwargs)
        return net(images)

    def collapsed_fn(self, images: jnp.ndarray, **kwargs) -> jnp.ndarray:
        net = self.collapsed(**kwargs)
        return net(images)

    def __init__(self, network: str):
        self.kwargs = get_sesr_args(network)
        self.expanded = sesr.SESR
        self.collapsed = sesr_c.SESR_Collapsed
        self.exp_transformed = hk.without_apply_rng(hk.transform(self.expanded_fn))
        self.col_transformed = hk.without_apply_rng(hk.transform(self.collapsed_fn))

    def init(self, *args):
        _ = self.col_transformed.init(*args, scale=2, **self.kwargs)
        return self.exp_transformed.init(*args, scale=2, **self.kwargs)

    def apply(self, params, images):
        return self.col_transformed.apply(collapse(params, **self.kwargs), images)