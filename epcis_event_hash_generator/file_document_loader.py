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
        "14b10c9d3e92d35f577bfc610fe5ec15aa2941124987919389d7cd9998516861",
        "https://ref.gs1.org/standards/epcis/2.0.0/epcis-context.jsonld":
        "e532647e8eb371379b8b0e8602d8981c8566bc60f7351f22c76a5bc865962008"
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
