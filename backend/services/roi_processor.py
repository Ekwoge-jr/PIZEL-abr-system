## Read ROI coordinates from PostgreSQL 
# Generate mask information
# Provide ROI data to encoder


from models import ROIConfig


def get_roi(lab_id):

    rois = ROIConfig.query.filter_by(r_lab_id=lab_id).all()

    result = []

    for roi in rois:
        result.append({ 
            "x": roi.x,
            "y": roi.y,
            "width": roi.width,
            "height": roi.height
        })


    return result