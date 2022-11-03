from .ten_forward import TenForwardSpider
from .hawks_and_reed import HawksAndReedSpider
from .guiding_star_grange import GuidingStarGrangeSpider
from .four_phantoms import FourPhantomsSpider

SPIDERS = {
    'ten-forward': TenForwardSpider,
    'hawks-and-reed': HawksAndReedSpider,
    'guiding-star-grange': GuidingStarGrangeSpider,
    'four-phantoms': FourPhantomsSpider,
}
