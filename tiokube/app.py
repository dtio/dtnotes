import os
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiokube.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---
class Cluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    nodes = db.relationship('Node', backref='cluster', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'nodes': [node.to_dict() for node in self.nodes]
        }

class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Waiting')
    cluster_id = db.Column(db.Integer, db.ForeignKey('cluster.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'hostname': self.hostname,
            'status': self.status
        }

# Define the main route for the dashboard
@app.route('/')
def home():
    """Renders the TioKube dashboard page."""
    return render_template("index.html")

@app.route('/cluster/<int:cluster_id>')
def manage_cluster(cluster_id):
    """Renders the page to manage a single cluster."""
    cluster = Cluster.query.get_or_404(cluster_id)
    return render_template("cluster.html", cluster=cluster, app_host=request.host)

# --- API Endpoints ---
@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    clusters = Cluster.query.all()
    return jsonify([cluster.to_dict() for cluster in clusters])

@app.route('/api/clusters', methods=['POST'])
def create_cluster():
    data = request.get_json()
    new_cluster = Cluster(name=data['name'])
    db.session.add(new_cluster)
    db.session.commit()
    return jsonify(new_cluster.to_dict()), 201

@app.route('/api/clusters/<int:cluster_id>/nodes', methods=['POST'])
def add_node_to_cluster(cluster_id):
    data = request.get_json()
    new_node = Node(hostname=data['hostname'], cluster_id=cluster_id)
    db.session.add(new_node)
    db.session.commit()
    return jsonify(new_node.to_dict()), 201

@app.route('/api/clusters/<int:cluster_id>', methods=['DELETE'])
def delete_cluster(cluster_id):
    cluster = Cluster.query.get_or_404(cluster_id)
    db.session.delete(cluster)
    db.session.commit()
    return jsonify({'message': 'Cluster deleted'}), 200

@app.route('/api/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    node = Node.query.get_or_404(node_id)
    db.session.delete(node)
    db.session.commit()
    return jsonify({'message': 'Node deleted'}), 200

@app.route('/api/nodes/<int:node_id>/status', methods=['PATCH'])
def update_node_status(node_id):
    """Updates the status of a node."""
    node = Node.query.get_or_404(node_id)
    data = request.get_json()
    node.status = data.get('status', 'Waiting')
    db.session.commit()
    return jsonify(node.to_dict())

@app.route('/api/cluster/<string:cluster_name>/<string:node_name>')
def generate_join_script(cluster_name, node_name):
    """Generates a bash script to join a node to the cluster."""
    cluster = Cluster.query.filter_by(name=cluster_name).first_or_404()
    node = Node.query.filter_by(hostname=node_name, cluster_id=cluster.id).first()

    if not node:
        return jsonify({"error": f"Node '{node_name}' not found in cluster '{cluster_name}'"}), 404

    # Get the host of the tiokube app to build the callback URL
    app_host = request.host

    script = f"""#!/bin/bash
set -e
set -x

echo "--- PREPARING NODE {node_name} TO JOIN CLUSTER {cluster_name} ---"

# Set sysctl params required by setup
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\\(.*\\)$/#\\1/g' /etc/fstab

# Set Selinux to Permissive
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

# Disable firewall
sudo systemctl disable firewalld --now

# Setup Repository
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install and configure containerd
dnf install -y containerd.io
containerd config default > /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
systemctl enable --now containerd

cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.32/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

# Install k8s tools
sudo dnf install -y kubelet kubeadm kubectl --disableexcludes=kubernetes

# Start kubelet service
sudo systemctl enable --now kubelet

echo "--- NODE PREPARATION COMPLETE ---"

# Report back to the tiokube app that the node is ready
echo "--- UPDATING NODE STATUS TO 'Ready' ---"
curl -X PATCH http://{app_host}/api/nodes/{node.id}/status \\
    -H "Content-Type: application/json" \\
    -d '{{"status": "Ready"}}'
"""

    return Response(script, mimetype='text/x-shellscript')


# This block allows running the app with 'python app.py'
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # The host is set to '0.0.0.0' to be accessible from outside the container
    app.run(host='0.0.0.0', port=5000, debug=True)