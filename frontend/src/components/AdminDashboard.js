import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  Shield, 
  LogOut, 
  BarChart3, 
  Activity, 
  TrendingUp, 
  Users,
  Calendar,
  MapPin,
  Loader2,
  RefreshCw
} from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { toast } from "sonner";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = ({ onLogout }) => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [logsResponse, statsResponse] = await Promise.all([
        axios.get(`${API}/logs`),
        axios.get(`${API}/stats`)
      ]);

      setLogs(logsResponse.data);
      setStats(statsResponse.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const getStatusBadgeVariant = (status) => {
    if (status === "valid") return "default";
    if (status === "expired") return "secondary";
    if (status === "fake") return "destructive";
    if (status === "suspected") return "outline";
    return "default";
  };

  const getStatusIcon = (status) => {
    const iconClass = "w-4 h-4";
    if (status === "valid") return <span className={`${iconClass} text-green-500`}>✅</span>;
    if (status === "expired") return <span className={`${iconClass} text-yellow-500`}>⚠️</span>;
    if (status === "fake") return <span className={`${iconClass} text-red-500`}>❌</span>;
    if (status === "suspected") return <span className={`${iconClass} text-orange-500`}>🤔</span>;
    return null;
  };

  // Chart data
  const pieChartData = stats ? {
    labels: Object.keys(stats.status_distribution).map(key => {
      return key.charAt(0).toUpperCase() + key.slice(1);
    }),
    datasets: [
      {
        data: Object.values(stats.status_distribution),
        backgroundColor: [
          '#10B981', // Valid - Green
          '#F59E0B', // Expired - Yellow
          '#EF4444', // Fake - Red
          '#F97316', // Suspected - Orange
        ],
        borderColor: [
          '#059669',
          '#D97706',
          '#DC2626',
          '#EA580C',
        ],
        borderWidth: 2,
      },
    ],
  } : null;

  const barChartData = stats ? {
    labels: stats.daily_verifications.map(item => {
      const date = new Date(item._id);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Daily Verifications',
        data: stats.daily_verifications.map(item => item.count),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        borderRadius: 4,
      },
    ],
  } : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'bottom',
      },
      title: {
        display: false,
      },
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-sm text-gray-500">Medicine Quality Monitor</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button variant="outline" onClick={onLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Verifications</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_verifications || 0}</div>
                <p className="text-xs text-muted-foreground">All time</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Valid Medicines</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {stats.status_distribution.valid || 0}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats.total_verifications > 0 
                    ? Math.round((stats.status_distribution.valid || 0) / stats.total_verifications * 100)
                    : 0}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Fake/Suspected</CardTitle>
                <BarChart3 className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {(stats.status_distribution.fake || 0) + (stats.status_distribution.suspected || 0)}
                </div>
                <p className="text-xs text-muted-foreground">Flagged items</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Database Size</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_medicines}</div>
                <p className="text-xs text-muted-foreground">Medicine records</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content */}
        <Tabs defaultValue="logs" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="logs">Verification Logs</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Logs Tab */}
          <TabsContent value="logs">
            <Card>
              <CardHeader>
                <CardTitle>Recent Verification Logs</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {logs.length === 0 ? (
                    <p className="text-center text-gray-500 py-8">No verification logs found</p>
                  ) : (
                    logs.slice(0, 20).map((log) => (
                      <div 
                        key={log.id} 
                        className="flex items-center justify-between p-4 border border-gray-200 rounded-lg bg-white hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center space-x-4">
                          {getStatusIcon(log.status)}
                          <div>
                            <p className="font-medium text-gray-900">
                              Batch: <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">{log.batch_code}</span>
                            </p>
                            <p className="text-sm text-gray-600">{log.reason}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <Badge variant={getStatusBadgeVariant(log.status)}>
                            {Math.round(log.confidence * 100)}% confidence
                          </Badge>
                          
                          {log.location && (
                            <div className="flex items-center text-xs text-gray-500">
                              <MapPin className="w-3 h-3 mr-1" />
                              {log.location.lat?.toFixed(2)}, {log.location.lng?.toFixed(2)}
                            </div>
                          )}
                          
                          <div className="flex items-center text-xs text-gray-500">
                            <Calendar className="w-3 h-3 mr-1" />
                            {new Date(log.timestamp).toLocaleDateString()} {new Date(log.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Status Distribution Pie Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Verification Status Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  {pieChartData ? (
                    <div className="h-64">
                      <Pie data={pieChartData} options={chartOptions} />
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      No data available
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Daily Verifications Bar Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Daily Verification Trends</CardTitle>
                </CardHeader>
                <CardContent>
                  {barChartData ? (
                    <div className="h-64">
                      <Bar data={barChartData} options={chartOptions} />
                    </div>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      No data available
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;