import collections
import itertools

from execution import PromptExecutor

from . import register_node


@register_node
class MakeJob:
    """Turns a sequence into a job with one attribute."""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "sequence": ("SEQUENCE", ),
                "name": ("STRING", {"default": ''}),
            },
        }

    RETURN_TYPES = ("JOB", "INT")
    RETURN_NAMES = ("job", "count")
    FUNCTION = "go"
    CATEGORY = "ali1234/job"

    def merge_dicts(self, *dicts):
        #return collections.ChainMap(*reversed(dicts))
        return dict(itertools.chain.from_iterable(d.items() for d in dicts))

    def go(self, sequence, name):
        result = [{name: value} for value in sequence]
        return (result, len(result))


@register_node
class CombineJobs(MakeJob):
    """Combines multiple jobs."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("JOB", ),
                "method": (("zip", "product"), {"default": "zip"}),
            },
            "optional": {
                x: ("JOB", ) for x in ('b', 'c', 'd', 'e')
            }
        }

    def go(self, method, **kwargs):
        method = {'product': itertools.product, 'zip': zip}[method]
        result = [self.merge_dicts(*steps) for steps in method(*kwargs.values())]
        return (result, len(result))


@register_node
class EnumerateJob(MakeJob):
    """Combines multiple jobs."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "job": ("JOB", ),
                "name": ("STRING", {"default": ''}),
            },
        }

    def go(self, job, name):
        result = [self.merge_dicts(step, {name: n}) for n, step in enumerate(job)]
        return (result, len(result))


@register_node
class GetJobStep:
    """Gets the job step by number."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "job": ("JOB", ),
                "step": ("INT", {"default": 0}),
                "wrap": (("repeat", "clamp"), {"default": "repeat"}),
            },
        }
    RETURN_TYPES = ("ATTRIBUTES", )
    RETURN_NAMES = ("attributes", )
    FUNCTION = "go"
    CATEGORY = "ali1234/job"

    def go(self, job, step, wrap):
        if wrap == 'repeat':
            while step < 0:
                step += len(job)
            step = step % len(job)
        elif wrap == 'clamp':
            step = max(min(step, len(job)), 0)
        return (job[step], )


@register_node
class FormatAttributes:
    """Applies attributes to a format string."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "attributes": ("ATTRIBUTES",),
                "format": ("STRING", {'default': '', 'multiline': True, "dynamicPrompts": False})
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("string", )
    FUNCTION = "go"
    CATEGORY = "ali1234/job"

    def go(self, attributes, format):
        return (format.format(**attributes), )


class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


@register_node
class GetAttribute:
    """Gets a named attribute from a step."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "attributes": ("ATTRIBUTES", ),
                "name": ("STRING", {"default": ''}),
            },
        }

    RETURN_TYPES = (AnyType("*"), )
    RETURN_NAMES = ("value", )
    FUNCTION = "go"
    CATEGORY = "ali1234/job"

    def go(self, attributes, name):
        return (attributes[name], )


# Dynamically register typed attribute getters to avoid wildcard bug
# https://github.com/comfyanonymous/ComfyUI/pull/770
for t in ('INT', 'FLOAT', 'STRING'):
    register_node(type(
        'GetAttribute'+t.title(),
        (GetAttribute, ),
        {
            'RETURN_TYPES': (t, ),
        }
    ))




@register_node
class JobToList:
    """Converts a job into a list."""
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "job": ("JOB",),
            },
        }

    RETURN_TYPES = ("ATTRIBUTES",)
    RETURN_NAMES = ("attributes",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "go"
    CATEGORY = "ali1234/job"

    def go(self, job):
        return (job,)
