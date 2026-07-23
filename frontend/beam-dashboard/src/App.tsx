import BeamHeatmapViewer from './components/BeamHeatmapViewer';
import LiveCharts from './components/LiveCharts';

export default function App() {
  return (
    <main>
      <h1>LaserSim Beam Dashboard</h1>
      <BeamHeatmapViewer />
      <LiveCharts />
    </main>
  );
}
