from services.roi_processor import get_roi


def build_roi_filter(lab_id):

    rois = get_roi(lab_id)

    if not rois:
        return ""

    filters = []

    for roi in rois:

        filters.append(
            (
                f"addroi="
                f"x={roi['x']}:"
                f"y={roi['y']}:"
                f"w={roi['width']}:"
                f"h={roi['height']}:"
                f"qoffset=-0.1"
            )
        )

    return ",".join(filters)