"""
File document loader with Requests fallback.

.. moduleauthor:: Sebastian Schmittner
"""
import logging
import importlib.resources
import json

from pyld.jsonld import JsonLdError


def file_document_loader(secure=False, **kwargs):
    """
    Create a File document loader.

    Forwarding arguments to requests document loader

    :param secure: require all requests to use HTTPS (default: False).
    :param **kwargs: extra keyword args for Requests get() call.

    :return: the RemoteDocument loader function.
    """
    from pyld import jsonld

    context_file_hashes = {
        "https://gs1.github.io/EPCIS/epcis-context.jsonld":
        "14b10c9d3e92d35f577bfc610fe5ec15aa2941124987919389d7cd9998516861.jsonld",
        "https://ref.gs1.org/standards/epcis/2.0.0/epcis-context.jsonld":
        "e532647e8eb371379b8b0e8602d8981c8566bc60f7351f22c76a5bc865962008.jsonld",
        "https://eecc.de/global_2025-09-26.jsonld":
        "d7b7387ef0ea28c725046d7c491218f0d765e84b58199cb4c1896516157f4fbb.jsonld",
        "https://ref.gs1.org/standards/epcis/epcis-context.jsonld":
        "5056c65f991425b1d3a35e35edf4f7d0c7ff56cf688c2912b930f93494713737.jsonld",
        "https://ref.gs1.org/standards/epcis/2.1.0/epcis-context.jsonld":
        "e8da7b13521f6ea2f469f7634086538575da899873055dda151997c72803fe1e.jsonld"
    }

    def loader(url, options={}):
        """
        Retrieves JSON-LD for the given name (URL).

        :return: the RemoteDocument.
        """

        try:
            if url in context_file_hashes:
                with importlib.resources.open_text("epcis_event_hash_generator", context_file_hashes[url]) as file:
                    data = json.load(file)

                doc = {
                    'contentType': 'application/ld+json',
                    'contextUrl': None,
                    'documentUrl': url,
                    'document': data
                }

                logging.debug("Loading %s from file", url)

                return doc

        except JsonLdError as e:
            raise e
        except Exception as cause:
            raise JsonLdError(
                'Could not retrieve a JSON-LD document.',
                'jsonld.LoadDocumentError', code='loading document failed',
                cause=cause)

        logging.debug("Fallback: Loading %s from the internet", url)
        request_loader = jsonld.requests_document_loader(secure=secure, **kwargs)
        return request_loader(url=url, options=options)

    return loader
