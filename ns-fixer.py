from hypernet.namespace.fixer import Fixer
import pprint

pp = pprint.PrettyPrinter()

fixer = Fixer()
srcDir = 'roadgen'
destDir = 'src/junctionart/roadgen'

# nsMap = fixer.buildNsMap(srcDir)
# pp.pprint(nsMap)

'''
{
   {'copy': 'copy',
 'dill': 'dill',
 'enum': 'enum',
 'extensions': 'extensions',
 'extensions.CountryCodes': 'extensions.CountryCodes',
 'extensions.ExtendedRoad': 'extensions.ExtendedRoad',
 'extensions.moreHelpers': 'extensions.moreHelpers',
 'glob': 'glob',
 'itertools': 'itertools',
 'junctions.Intersection': 'junctions.Intersection',
 'junctions.IntersectionValidator': 'junctions.IntersectionValidator',
 'junctions.JunctionBuilderFromPointsAndHeading': 'junctions.JunctionBuilderFromPointsAndHeading',
 'junctions.LaneBuilder': 'junctions.LaneBuilder',
 'junctions.LaneConfiguration': 'junctions.LaneConfiguration',
 'junctions.LaneLinker': 'junctions.LaneLinker',
 'junctions.LaneMarkGenerator': 'junctions.LaneMarkGenerator',
 'junctions.LaneSides': 'junctions.LaneSides',
 'junctions.ODRHelper': 'junctions.ODRHelper',
 'junctions.RoadBuilder': 'junctions.RoadBuilder',
 'junctions.RoadLinker': 'junctions.RoadLinker',
 'junctions.SequentialJunctionBuilder': 'junctions.SequentialJunctionBuilder',
 'library.Combinator': 'library.Combinator',
 'library.Configuration': 'library.Configuration',
 'logging': 'logging',
 'logging,': 'logging,',
 'math': 'math',
 'math,': 'math,',
 'matplotlib': 'matplotlib',
 'matplotlib.pyplot': 'matplotlib.pyplot',
 'matplotlib.ticker': 'matplotlib.ticker',
 'numpy': 'numpy',
 'numpy.core.numeric': 'numpy.core.numeric',
 'os.path': 'os.path',
 'pyodrx': 'pyodrx',
 'pyodrx,': 'pyodrx,',
 'pyodrx.enumerations': 'pyodrx.enumerations',
 'random': 'random',
 'roadgen.controlLine.ControlLine': 'roadgen.controlLine.ControlLine',
 'roadgen.controlLine.ControlLineGrid': 'roadgen.controlLine.ControlLineGrid',
 'roadgen.controlLine.ControlPoint': 'roadgen.controlLine.ControlPoint',
 'roadgen.controlLine.ControlPointIntersectionAdapter': 'roadgen.controlLine.ControlPointIntersectionAdapter',
 'roadgen.definitions.DirectionIntersection': 'roadgen.definitions.DirectionIntersection',
 'roadgen.definitions.DirectionQuadrant': 'roadgen.definitions.DirectionQuadrant',
 'roadgen.definitions.EmptySpace': 'roadgen.definitions.EmptySpace',
 'roadgen.definitions.LineSegment': 'roadgen.definitions.LineSegment',
 'roadgen.definitions.Point': 'roadgen.definitions.Point',
 'roadgen.definitions.Polygon': 'roadgen.definitions.Polygon',
 'roadgen.layout.BoundaryException': 'roadgen.layout.BoundaryException',
 'roadgen.layout.Cell': 'roadgen.layout.Cell',
 'roadgen.layout.Grid': 'roadgen.layout.Grid',
 'roadgen.layout.IntersectionAdapter': 'roadgen.layout.IntersectionAdapter',
 'roadgen.layout.MapBuilder': 'roadgen.layout.MapBuilder',
 'roadgen.layout.Network': 'roadgen.layout.Network',
 'roadgen.layout.NotEmptyException': 'roadgen.layout.NotEmptyException',
 'roadgen.layout.PerlinNoise': 'roadgen.layout.PerlinNoise',
 'roadgen.layout.QuadrantSolver': 'roadgen.layout.QuadrantSolver',
 'roadgen.library.ValueConverter': 'roadgen.library.ValueConverter',
 'skspatial.objects': 'skspatial.objects',
 'traceback': 'traceback',
 'typing': 'typing',
 'z3': 'z3'
}

'''

nsMap = {
  'roadgen': 'junctionart.roadgen',
  'junctions': 'junctionart.junctions',
  'extensions': 'junctionart.extensions',
}

fixer.run(packageSrcDir=srcDir, packageOutputDir=destDir, nsMap=nsMap)
