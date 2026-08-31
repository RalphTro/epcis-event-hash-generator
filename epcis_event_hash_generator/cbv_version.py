from dataclasses import dataclass

@dataclass(frozen=True)
class VersionProfile:
    # 2.1: extensions inline within parent; 2.0: prefixed + appended at end
    inline_user_extensions: bool

    # 2.1: include "sensorElementList" wrapper; 2.0: omit it
    keep_sensor_element_list: bool

    # "?ver=CBV2.0" / "?ver=CBV2.1"
    uri_suffix: str

PROFILES = {
    "CBV2.0": VersionProfile(inline_user_extensions=False, keep_sensor_element_list=False, uri_suffix="?ver=CBV2.0"),
    "CBV2.1": VersionProfile(inline_user_extensions=True, keep_sensor_element_list=True, uri_suffix="?ver=CBV2.1"),
}
DEFAULT_VERSION = "CBV2.0"

def profile_for(version):
    return PROFILES.get(version, PROFILES[DEFAULT_VERSION])