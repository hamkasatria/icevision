"""
How to train MaskRCNN, using the [Penn-Fundan](https://www.cis.upenn.edu/~jshi/ped_html/) dataset.
"""

# Install mantisshrimp
# pip install git+git://github.com/airctic/mantisshrimp.git@train_mask#egg=mantisshrimp[all] --upgrade

# Import everything from mantisshrimp
from mantisshrimp.all import *

# Load the data and create the parser
data_dir = datasets.pennfundan.load()
class_map = datasets.pennfundan.class_map()
parser = datasets.pennfundan.parser(data_dir)

# Parse records with random splits
data_splitter = RandomSplitter([0.8, 0.2])
train_records, valid_records = parser.parse(data_splitter)

# Define the transforms and create the Datasets
presize = 512
size = 384
train_tfms = tfms.A.Adapter(
    [*tfms.A.aug_tfms(size=size, presize=presize), tfms.A.Normalize()]
)
valid_tfms = tfms.A.Adapter([*tfms.A.resize_and_pad(size=size), tfms.A.Normalize()])
train_ds = Dataset(train_records, train_tfms)
valid_ds = Dataset(valid_records, valid_tfms)

# Shows how the transforms affects a single sample
samples = [train_ds[0] for _ in range(6)]
show_samples(
    samples, denormalize_fn=denormalize_imagenet, ncols=3, label=False, show=True
)

# Create DataLoaders
train_dl = mask_rcnn.train_dl(train_ds, batch_size=16, shuffle=True, num_workers=4)
valid_dl = mask_rcnn.valid_dl(valid_ds, batch_size=16, shuffle=False, num_workers=4)

# Define metrics for the model
# TODO: Currently broken for Mask RCNN
# metrics = [COCOMetric(COCOMetricType.mask)]

# Create model
model = mask_rcnn.model(num_classes=len(class_map))

# Create Learner and train
learn = mask_rcnn.fastai.learner(model=model)
learn.fine_tune(10, 5e-4, freeze_epochs=2)

# BONUS: Use model for inference. In this case, let's take some images from valid_ds
# Take a look at `Dataset.from_images` if you want to predict from images in memory
samples = [valid_ds[i] for i in range(6)]
batch, samples = mask_rcnn.build_infer_batch(samples)
preds = mask_rcnn.predict(model=model, batch=batch)

imgs = [sample["img"] for sample in samples]
show_preds(imgs=imgs, preds=preds, denormalize_fn=denormalize_imagenet, ncols=3)
