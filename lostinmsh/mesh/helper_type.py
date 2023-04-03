"""Domain."""


from typing import NamedTuple, TypeAlias

NodeTag: TypeAlias = int
NodeTags: TypeAlias = list[NodeTag]

CurveTag: TypeAlias = int
CurveTags: TypeAlias = list[CurveTag]

LoopTag: TypeAlias = int
LoopTags: TypeAlias = list[LoopTag]

SurfaceTag: TypeAlias = int
SurfaceTags: TypeAlias = list[SurfaceTag]

Tags: TypeAlias = list[int]


class Domain(NamedTuple):
    """Domain."""

    name: str
    dim: int


DomainTags: TypeAlias = dict[Domain, Tags]


def update_domain_tags(domain_tags: DomainTags, dom_tags_to_add: DomainTags) -> None:
    """Update DomainTags with dom_tags_to_add.

    Parameters
    ----------
    domain_tags : DomainTags
        update domain_tags
    dom_tags_to_add : DomainTags
        domain tags to add
    """
    for dom, tags in dom_tags_to_add.items():
        if dom in domain_tags:
            domain_tags[dom].extend(tags)
        else:
            domain_tags[dom] = tags
