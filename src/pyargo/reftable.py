# -*coding: UTF-8 -*-
__author__ = 'guillaumemaze'

def table4(code):
    """Reference table 4: history action codes"""
    if not isinstance(code, str):
        try:
            code = code.astype(str).tostring().strip()
        except:
            code = code.astype(str).values.tostring().strip()

    if code == 'AO':
        return "AOML, USA"
    elif code=="BO":
        return "BODC, United Kingdom"
    elif code=="CI":
        return "Institute of Ocean Sciences, Canada"
    elif code=="CS":
        return "CSIRO, Australia"
    elif code=="GE":
        return "BSH, Germany"
    elif code=="GT":
        return "GTS: used for data coming from WMO GTS network"
    elif code=="HZ":
        return "CSIO, China Second Institute of Oceanography"
    elif code=="IF":
        return "Ifremer, France"
    elif code=="IN":
        return "INCOIS, India"
    elif code=="JA":
        return "JMA, Japan"
    elif code=="JM":
        return "Jamstec, Japan"
    elif code=="KM":
        return "KMA, Korea"
    elif code=="KO":
        return "KORDI, Korea"
    elif code=="MB":
        return "MBARI, USA"
    elif code=="ME":
        return "MEDS, Canada"
    elif code=="NA":
        return "NAVO, USA"
    elif code=="NM":
        return "NMDIS, China"
    elif code=="PM":
        return "PMEL, USA"
    elif code=="RU":
        return "Russia"
    elif code=="SI":
        return "SIO, Scripps, USA"
    elif code=="SP":
        return "Spain"
    elif code=="UW":
        return "University of Washington, USA"
    elif code=="VL":
        return "Far Eastern Regional Hydrometeorological Research Institute of Vladivostock, Russia"
    elif code=="WH":
        return "Woods Hole Oceanographic Institution, USA"
    elif len(code) == 0:
        return "Empty string!"
    else:
        return "Unknown code for table 4!"

# dac = {'KM':'kma',
#        'IF':'coriolis',
#        'AO':'aoml',
#        'CS':'csiro',
#        'KO':'kordi',
#        'JA':'jma',
#        'HZ':'csio',
#        'IN':'incois',
#        'NM':'nmdis',
#        'ME':'meds',
#        'BO':'bodc'}

def table7(code):
    """Reference table 7: history action codes"""
    try:
        code = code.astype(str).tostring().strip()
    except:
        code = code.astype(str).values.tostring().strip()

    if code == 'CF':
        return "Change a quality flag"
    elif code=="CR":
        return "Create record"
    elif code=="CV":
        return "Change value"
    elif code=="DC":
        return "Station was checked by duplicate checking software"
    elif code=="ED":
        return "Edit a parameter value"
    elif code=="IP":
        return "This history group operates on the complete input record"
    elif code=="NG":
        return "No good trace"
    elif code=="PE":
        return "Position error. Profile position has been erroneously encoded. Corrected if possible."
    elif code=="QC":
        return "Quality Control"
    elif code=="QCF$":
        return "Tests failed"
    elif code=="QCP$":
        return "Test performed"
    elif code=="SV":
        return "Set a value"
    elif code=="TE":
        return "Time error. Profile data/time has been erroneously encoded. correct if possible"
    elif code=="UP":
        return "Station passed through the update program"
    elif len(code) == 0:
        return "Empty string!"
    else:
        return "Unknown code for table 7!"

def table12(code):
    """Reference table 12: history steps codes"""
    try:
        code = code.astype(str).tostring().strip()
    except:
        code = code.astype(str).values.tostring().strip()

    if code == "ARFM":
        return "Convert raw data from telecommunications system to a processing format"
    elif code == "ARGQ":
        return "Automatic QC of data reported in real-time has been performed"
    elif code == "IGO3":
        return "Checking for duplicates has been performed"
    elif code == "ARSQ":
        return "Delayed mode QC has been performed"
    elif code == "ARCA":
        return "Calibration has been performed"
    elif code == "ARUP":
        return "Real-time data have been archived locally and sent to GDACs"
    elif code == "ARDU":
        return "Delayed data have been archived locally and sent to GDACs"
    elif code == "RFMT":
        return "Reformat software to convert hexadecimal format reported by the buoy to our standard format"
    elif code == "COOA":
        return "Coriolis objective analysis performed"
    elif len(code) == 0:
        return "Empty string!"
    else:
        return "Unknown code for table 12!"