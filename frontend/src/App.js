import React, { useState, useEffect } from 'react';
import './App.css';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { ScrollArea } from './components/ui/scroll-area';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Input } from './components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Label } from './components/ui/label';
import { Textarea } from './components/ui/textarea';
import { 
  Play, 
  Square, 
  Plus, 
  Trash2, 
  Activity, 
  Database, 
  Globe, 
  Server, 
  Cpu, 
  MemoryStick,
  Clock,
  Terminal,
  Smartphone,
  BarChart3,
  Zap,
  RefreshCw,
  Search,
  Filter,
  TrendingUp,
  Eye,
  Settings
} from 'lucide-react';

const App = () => {
  const [environments, setEnvironments] = useState([]);
  const [selectedEnv, setSelectedEnv] = useState(null);
  const [serviceLogs, setServiceLogs] = useState({});
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newEnv, setNewEnv] = useState({ name: '', stack_type: '', description: '' });
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    running: 0,
    stopped: 0,
    services: 0
  });

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = backendUrl.replace('https://', 'wss://').replace('http://', 'ws://');
      const websocket = new WebSocket(`${wsUrl}/api/ws`);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };
      
      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('WebSocket message:', data);
        
        if (data.type === 'metrics_update') {
          fetchEnvironments(); // Refresh data on metrics update
        }
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      setWs(websocket);
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [backendUrl]);

  // Fetch environments on component mount
  useEffect(() => {
    fetchEnvironments();
  }, []);

  const fetchEnvironments = async () => {
    try {
      setRefreshing(true);
      const response = await fetch(`${backendUrl}/api/environments`);
      if (response.ok) {
        const data = await response.json();
        setEnvironments(data);
        
        // Calculate statistics
        const totalServices = data.reduce((acc, env) => acc + env.services.length, 0);
        const runningEnvs = data.filter(env => env.status === 'running').length;
        const stoppedEnvs = data.filter(env => env.status === 'stopped').length;
        
        setStats({
          total: data.length,
          running: runningEnvs,
          stopped: stoppedEnvs,
          services: totalServices
        });
      }
    } catch (error) {
      console.error('Error fetching environments:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const createEnvironment = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${backendUrl}/api/environments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newEnv),
      });
      
      if (response.ok) {
        setIsCreateDialogOpen(false);
        setNewEnv({ name: '', stack_type: '', description: '' });
        fetchEnvironments();
      }
    } catch (error) {
      console.error('Error creating environment:', error);
    }
  };

  const startEnvironment = async (envId) => {
    try {
      await fetch(`${backendUrl}/api/environments/${envId}/start`, { method: 'PUT' });
      fetchEnvironments();
    } catch (error) {
      console.error('Error starting environment:', error);
    }
  };

  const stopEnvironment = async (envId) => {
    try {
      await fetch(`${backendUrl}/api/environments/${envId}/stop`, { method: 'PUT' });
      fetchEnvironments();
    } catch (error) {
      console.error('Error stopping environment:', error);
    }
  };

  const deleteEnvironment = async (envId) => {
    if (window.confirm('Are you sure you want to delete this environment?')) {
      try {
        await fetch(`${backendUrl}/api/environments/${envId}`, { method: 'DELETE' });
        fetchEnvironments();
      } catch (error) {
        console.error('Error deleting environment:', error);
      }
    }
  };

  const toggleService = async (serviceId) => {
    try {
      await fetch(`${backendUrl}/api/services/${serviceId}/toggle`, { method: 'PUT' });
      fetchEnvironments();
    } catch (error) {
      console.error('Error toggling service:', error);
    }
  };

  const fetchServiceLogs = async (serviceId) => {
    try {
      const response = await fetch(`${backendUrl}/api/services/${serviceId}/logs`);
      if (response.ok) {
        const logs = await response.json();
        setServiceLogs(prev => ({ ...prev, [serviceId]: logs }));
      }
    } catch (error) {
      console.error('Error fetching service logs:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-green-500';
      case 'stopped': return 'bg-gray-500';
      case 'error': return 'bg-red-500';
      case 'partial': return 'bg-yellow-500';
      default: return 'bg-gray-400';
    }
  };

  const getServiceIcon = (type) => {
    switch (type) {
      case 'database': return <Database className="h-4 w-4" />;
      case 'web': return <Globe className="h-4 w-4" />;
      case 'api': return <Server className="h-4 w-4" />;
      case 'cache': return <Activity className="h-4 w-4" />;
      case 'runtime': return <Zap className="h-4 w-4" />;
      default: return <Server className="h-4 w-4" />;
    }
  };

  // Filter environments based on search and status
  const filteredEnvironments = environments.filter(env => {
    const matchesSearch = env.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         env.stack_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === 'all' || env.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const startAllEnvironments = async () => {
    for (const env of environments) {
      if (env.status === 'stopped') {
        await startEnvironment(env.id);
      }
    }
  };

  const stopAllEnvironments = async () => {
    for (const env of environments) {
      if (env.status === 'running') {
        await stopEnvironment(env.id);
      }
    }
  };

  const stackTypes = ['LAMP', 'MEAN', 'Django', 'FastAPI', 'Next.js', 'Vue.js'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Enhanced Mobile Header with Stats */}
      <div className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Smartphone className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">DevStack Manager</h1>
              <div className="flex items-center space-x-4 text-xs text-slate-400">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                  <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <BarChart3 className="h-3 w-3" />
                  <span>{stats.total} envs</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button
              onClick={fetchEnvironments}
              className="bg-slate-700 hover:bg-slate-600 text-white p-2"
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            </Button>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white px-6">
                  <Plus className="h-4 w-4 mr-2" />
                  New
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-800 text-white border-slate-700">
                <DialogHeader>
                  <DialogTitle>Create New Environment</DialogTitle>
                  <DialogDescription className="text-slate-400">
                    Set up a new development stack environment
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={createEnvironment} className="space-y-4">
                  <div>
                    <Label htmlFor="name" className="text-sm font-medium text-slate-200">Name</Label>
                    <Input
                      id="name"
                      placeholder="My Dev Environment"
                      value={newEnv.name}
                      onChange={(e) => setNewEnv({ ...newEnv, name: e.target.value })}
                      className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="stack" className="text-sm font-medium text-slate-200">Stack Type</Label>
                    <Select 
                      value={newEnv.stack_type} 
                      onValueChange={(value) => setNewEnv({ ...newEnv, stack_type: value })}
                      required
                    >
                      <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                        <SelectValue placeholder="Choose a stack" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        {stackTypes.map(stack => (
                          <SelectItem key={stack} value={stack} className="text-white hover:bg-slate-600">
                            {stack}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="description" className="text-sm font-medium text-slate-200">Description</Label>
                    <Textarea
                      id="description"
                      placeholder="Brief description of this environment..."
                      value={newEnv.description}
                      onChange={(e) => setNewEnv({ ...newEnv, description: e.target.value })}
                      className="bg-slate-700 border-slate-600 text-white placeholder-slate-400"
                    />
                  </div>
                  <div className="flex space-x-3 pt-4">
                    <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700">
                      Create Environment
                    </Button>
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={() => setIsCreateDialogOpen(false)}
                      className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-700"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Statistics Dashboard */}
        <div className="px-4 pb-4">
          <div className="grid grid-cols-4 gap-3 mb-4">
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <div className="text-blue-400 text-lg font-bold">{stats.total}</div>
              <div className="text-xs text-slate-400">Total</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <div className="text-green-400 text-lg font-bold">{stats.running}</div>
              <div className="text-xs text-slate-400">Running</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <div className="text-gray-400 text-lg font-bold">{stats.stopped}</div>
              <div className="text-xs text-slate-400">Stopped</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3 text-center">
              <div className="text-yellow-400 text-lg font-bold">{stats.services}</div>
              <div className="text-xs text-slate-400">Services</div>
            </div>
          </div>

          {/* Search and Filter Controls */}
          <div className="flex space-x-3 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search environments..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-700 border-slate-600 text-white placeholder-slate-400 pl-10"
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-24 bg-slate-700 border-slate-600 text-white">
                <Filter className="h-4 w-4" />
              </SelectTrigger>
              <SelectContent className="bg-slate-700 border-slate-600">
                <SelectItem value="all" className="text-white">All</SelectItem>
                <SelectItem value="running" className="text-white">Running</SelectItem>
                <SelectItem value="stopped" className="text-white">Stopped</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Quick Actions */}
          {environments.length > 0 && (
            <div className="flex space-x-2">
              <Button 
                onClick={startAllEnvironments}
                className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm py-2"
              >
                <Play className="h-3 w-3 mr-2" />
                Start All
              </Button>
              <Button 
                onClick={stopAllEnvironments}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm py-2"
              >
                <Square className="h-3 w-3 mr-2" />
                Stop All
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4 pb-20">
        {environments.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <Server className="h-8 w-8 text-slate-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No Environments</h3>
            <p className="text-slate-400 mb-6">Create your first development environment to get started</p>
            <Button 
              onClick={() => setIsCreateDialogOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Environment
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {environments.map((env) => (
              <Card key={env.id} className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-white flex items-center space-x-3">
                        <span>{env.name}</span>
                        <Badge 
                          variant="secondary" 
                          className={`${getStatusColor(env.status)} text-white text-xs px-2 py-1`}
                        >
                          {env.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription className="text-slate-400 text-sm">
                        {env.stack_type} • {env.services.length} services
                      </CardDescription>
                      {env.description && (
                        <p className="text-slate-300 text-sm mt-2">{env.description}</p>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      {env.status === 'running' ? (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => stopEnvironment(env.id)}
                          className="border-red-500 text-red-400 hover:bg-red-500 hover:text-white"
                        >
                          <Square className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => startEnvironment(env.id)}
                          className="bg-green-600 hover:bg-green-700 text-white"
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => deleteEnvironment(env.id)}
                        className="border-red-500 text-red-400 hover:bg-red-500 hover:text-white"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <Tabs defaultValue="services" className="w-full">
                    <TabsList className="grid w-full grid-cols-2 bg-slate-700">
                      <TabsTrigger value="services" className="text-slate-200">Services</TabsTrigger>
                      <TabsTrigger value="logs" className="text-slate-200">Logs</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="services" className="mt-4">
                      <div className="space-y-3">
                        {env.services.map((service) => (
                          <div
                            key={service.id}
                            className="bg-slate-700/50 rounded-lg p-4 border border-slate-600"
                          >
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-3">
                                {getServiceIcon(service.type)}
                                <div>
                                  <h4 className="text-white font-medium text-sm">{service.name}</h4>
                                  <p className="text-slate-400 text-xs">Port {service.port}</p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge 
                                  variant="secondary" 
                                  className={`${getStatusColor(service.status)} text-white text-xs`}
                                >
                                  {service.status}
                                </Badge>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => toggleService(service.id)}
                                  className="border-slate-500 text-slate-300 hover:bg-slate-600 h-7 w-7 p-0"
                                >
                                  {service.status === 'running' ? (
                                    <Square className="h-3 w-3" />
                                  ) : (
                                    <Play className="h-3 w-3" />
                                  )}
                                </Button>
                              </div>
                            </div>
                            
                            {service.status === 'running' && (
                              <div className="grid grid-cols-3 gap-4 mt-3">
                                <div className="bg-slate-800/50 rounded p-2 text-center">
                                  <div className="flex items-center justify-center mb-1">
                                    <Cpu className="h-3 w-3 text-blue-400 mr-1" />
                                    <span className="text-xs text-slate-400">CPU</span>
                                  </div>
                                  <p className="text-sm font-bold text-white">{service.cpu_usage}%</p>
                                </div>
                                <div className="bg-slate-800/50 rounded p-2 text-center">
                                  <div className="flex items-center justify-center mb-1">
                                    <MemoryStick className="h-3 w-3 text-green-400 mr-1" />
                                    <span className="text-xs text-slate-400">RAM</span>
                                  </div>
                                  <p className="text-sm font-bold text-white">{service.memory_usage}%</p>
                                </div>
                                <div className="bg-slate-800/50 rounded p-2 text-center">
                                  <div className="flex items-center justify-center mb-1">
                                    <Clock className="h-3 w-3 text-yellow-400 mr-1" />
                                    <span className="text-xs text-slate-400">Up</span>
                                  </div>
                                  <p className="text-sm font-bold text-white">{service.uptime}</p>
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="logs" className="mt-4">
                      <div className="space-y-2">
                        {env.services.map((service) => (
                          <div key={service.id}>
                            <Button
                              variant="outline"
                              className="w-full justify-between text-left border-slate-600 text-slate-300 hover:bg-slate-700"
                              onClick={() => fetchServiceLogs(service.id)}
                            >
                              <div className="flex items-center space-x-2">
                                <Terminal className="h-4 w-4" />
                                <span>{service.name} logs</span>
                              </div>
                              <Badge variant="secondary" className="bg-slate-600 text-slate-200">
                                {serviceLogs[service.id]?.length || 0}
                              </Badge>
                            </Button>
                            
                            {serviceLogs[service.id] && (
                              <ScrollArea className="h-48 bg-slate-900/50 rounded border border-slate-600 mt-2">
                                <div className="p-3 space-y-1">
                                  {serviceLogs[service.id].map((log, idx) => (
                                    <div key={idx} className="text-xs">
                                      <span className={`inline-block w-16 font-mono ${
                                        log.level === 'error' ? 'text-red-400' :
                                        log.level === 'warning' ? 'text-yellow-400' :
                                        'text-green-400'
                                      }`}>
                                        [{log.level.toUpperCase()}]
                                      </span>
                                      <span className="text-slate-300 ml-2">{log.message}</span>
                                    </div>
                                  ))}
                                </div>
                              </ScrollArea>
                            )}
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;