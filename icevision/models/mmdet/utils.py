__all__ = [
    "mmdet_base_url",
    "param_groups",
    "MMDetBackboneConfig",
    "create_model_config",
]

from icevision.imports import *
from icevision.utils import *
from mmdet.models.detectors import *
from mmcv import Config

# mmdet_base_url = Path(
#     "https://raw.githubusercontent.com/open-mmlab/mmdetection/v2.10.0"
# )

mmdet_base_url = Path("mmdet")


def param_groups(model):
    body = model.backbone

    layers = []
    layers += [nn.Sequential(body.conv1, body.bn1)]
    layers += [getattr(body, l) for l in body.res_layers]
    layers += [model.neck]

    if isinstance(model, SingleStageDetector):
        layers += [model.bbox_head]
    elif isinstance(model, TwoStageDetector):
        layers += [nn.Sequential(model.rpn_head, model.roi_head)]
    else:
        raise RuntimeError(
            "{model} must inherit either from SingleStageDetector or TwoStageDetector class"
        )

    _param_groups = [list(layer.parameters()) for layer in layers]
    check_all_model_params_in_groups2(model, _param_groups)
    return _param_groups


@dataclass
class MMDetBackboneConfig:
    model_name: str
    cfg_url: str
    weights_url: str


def create_model_config(
    backbone: MMDetBackboneConfig,
    pretrained: bool = True,
    checkpoints_path: Optional[Union[str, Path]] = "checkpoints",
    force_download=False,
):

    model_name = backbone.model_name
    cfg_url = backbone.cfg_url
    weights_url = backbone.weights_url

    # download weights
    if pretrained and weights_url:
        save_dir = Path(checkpoints_path) / model_name
        save_dir.mkdir(exist_ok=True, parents=True)

        fname = Path(weights_url).name
        weights_path = save_dir / fname

        if not weights_path.exists() or force_download:
            download_url(url=weights_url, save_path=str(weights_path))

    cfg = Config.fromfile(cfg_url)

    return cfg, weights_path