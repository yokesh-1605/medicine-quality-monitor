import React, { useState } from "react";
import axios from "axios";
import { Shield, Search, AlertCircle, CheckCircle, XCircle, HelpCircle, Loader2 } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [batchCode, setBatchCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const getStatusIcon = (status) => {
    if (status.includes("Valid")) return <CheckCircle className="w-6 h-6 text-emerald-500" />;
    if (status.includes("Expired")) return <AlertCircle className="w-6 h-6 text-amber-500" />;
    if (status.includes("Fake")) return <XCircle className="w-6 h-6 text-red-500" />;
    if (status.includes("Suspected")) return <HelpCircle className="w-6 h-6 text-orange-500" />;
    return <Shield className="w-6 h-6 text-gray-500" />;
  };

  const getStatusColor = (status) => {
    if (status.includes("Valid")) return "bg-emerald-50 border-emerald-200 text-emerald-800";
    if (status.includes("Expired")) return "bg-amber-50 border-amber-200 text-amber-800";
    if (status.includes("Fake")) return "bg-red-50 border-red-200 text-red-800";
    if (status.includes("Suspected")) return "bg-orange-50 border-orange-200 text-orange-800";
    return "bg-gray-50 border-gray-200 text-gray-800";
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    
    if (!batchCode.trim()) {
      toast.error("Please enter a batch code");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Get user's location (optional)
      let location = {};
      if (navigator.geolocation) {
        const position = await new Promise((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
        }).catch(() => null);
        
        if (position) {
          location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
        }
      }

      const response = await axios.post(`${API}/verify`, {
        code: batchCode.trim(),
        ...location
      });

      setResult(response.data);
      
      // Show toast based on result
      if (response.data.status.includes("Valid")) {
        toast.success("Medicine verified as authentic!");
      } else if (response.data.status.includes("Expired")) {
        toast.warning("Medicine is expired!");
      } else {
        toast.error("Medicine verification failed!");
      }

    } catch (error) {
      console.error("Verification error:", error);
      toast.error("Failed to verify medicine. Please try again.");
      setResult({
        status: "Error ❌",
        reason: "Unable to connect to verification service",
        confidence: 0
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">Medicine Quality Monitor</h1>
            </div>
            <a
              href="/admin/login"
              className="text-sm text-gray-600 hover:text-blue-600 transition-colors"
            >
              Admin Portal
            </a>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Verify Medicine Authenticity
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Enter your medicine batch code to instantly verify its authenticity, 
            expiry status, and safety using our AI-powered detection system.
          </p>
        </div>

        {/* Verification Form */}
        <Card className="mb-8 shadow-lg border-0 bg-white/70 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-gray-900">
              <Search className="w-5 h-5" />
              <span>Batch Code Verification</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerify} className="space-y-4">
              <div>
                <label htmlFor="batchCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Medicine Batch Code
                </label>
                <Input
                  id="batchCode"
                  type="text"
                  placeholder="Enter batch code (e.g., MED123456A)"
                  value={batchCode}
                  onChange={(e) => setBatchCode(e.target.value.toUpperCase())}
                  className="text-lg h-12"
                  disabled={loading}
                />
                <p className="text-sm text-gray-500 mt-1">
                  Usually found on the medicine packaging or QR code
                </p>
              </div>
              
              <Button 
                type="submit" 
                disabled={loading || !batchCode.trim()}
                className="w-full h-12 text-lg bg-blue-600 hover:bg-blue-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5 mr-2" />
                    Verify Medicine
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Verification Result */}
        {result && (
          <Card className={`shadow-lg border-2 ${getStatusColor(result.status)}`}>
            <CardHeader>
              <CardTitle className="flex items-center space-x-3">
                {getStatusIcon(result.status)}
                <span className="text-xl">{result.status}</span>
                <Badge variant="secondary" className="ml-auto">
                  {Math.round(result.confidence * 100)}% confidence
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Verification Details</h4>
                <p className="text-gray-700">{result.reason}</p>
              </div>

              {result.batch_info && (
                <div className="bg-white/50 rounded-lg p-4 space-y-2">
                  <h4 className="font-semibold text-gray-900">Medicine Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-600">Name:</span>
                      <span className="ml-2 text-gray-900">{result.batch_info.name}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Manufacturer:</span>
                      <span className="ml-2 text-gray-900">{result.batch_info.manufacturer}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Expiry Date:</span>
                      <span className="ml-2 text-gray-900">
                        {new Date(result.batch_info.expiry_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Scan Count:</span>
                      <span className="ml-2 text-gray-900">{result.batch_info.scan_count}</span>
                    </div>
                  </div>
                </div>
              )}

              {result.status.includes("Suspected") && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <h4 className="font-semibold text-orange-800 mb-2">⚠️ Important Notice</h4>
                  <p className="text-orange-700 text-sm">
                    Our AI system has detected unusual patterns associated with this batch. 
                    While this doesn't confirm counterfeiting, we recommend consulting with 
                    a healthcare professional or pharmacist before use.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* How It Works Section */}
        <div className="mt-16 bg-white/50 backdrop-blur-sm rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">1. Enter Batch Code</h4>
              <p className="text-gray-600 text-sm">
                Input the batch code found on your medicine packaging
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">2. AI Analysis</h4>
              <p className="text-gray-600 text-sm">
                Our AI system checks the database and detects anomalies
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">3. Get Results</h4>
              <p className="text-gray-600 text-sm">
                Receive instant verification with detailed confidence scores
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;