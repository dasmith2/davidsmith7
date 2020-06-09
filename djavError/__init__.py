# You can't put from djavError.models import log_error in here because that
# causes a bootstrapping problem in djaveClass/models/base_knows_child.py When
# you try to import ContentType you get AppRegistryNotReady.
