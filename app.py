import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from supabase import create_client, Client
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Supabase configuration
SUPABASE_URL = "https://dtpszuxlofjlvbqqxsep.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR0cHN6dXhsb2ZqbHZicXF4c2VwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2ODYwMDQsImV4cCI6MjA3ODI2MjAwNH0.IkoWex28S5iQByQ7aGFeF4NpBAV3BuyluH_gN8qIEdE"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def dashboard():
    """Main dashboard showing overview"""
    try:
        # Get counts for dashboard
        l1_count = supabase.table('L1PromptDetails').select('*', count='exact').execute().count
        l2_count = supabase.table('L2PromptDetails').select('*', count='exact').execute().count
        
        # Get recent prompts
        recent_l1 = supabase.table('L1PromptDetails')\
            .select('*')\
            .order('CreatedOn', desc=True)\
            .limit(5)\
            .execute()
        
        recent_l2 = supabase.table('L2PromptDetails')\
            .select('*, L1PromptDetails(L1_Prompt)')\
            .order('CreatedOn', desc=True)\
            .limit(5)\
            .execute()
        
        return render_template('dashboard.html', 
                             l1_count=l1_count, 
                             l2_count=l2_count,
                             recent_l1=recent_l1.data if recent_l1.data else [],
                             recent_l2=recent_l2.data if recent_l2.data else [])
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', l1_count=0, l2_count=0, recent_l1=[], recent_l2=[])

@app.route('/l1-prompts')
def l1_prompts():
    """View all L1 prompts"""
    try:
        search = request.args.get('search', '')
        client_filter = request.args.get('client', '')
        
        query = supabase.table('L1PromptDetails')\
            .select('*')\
            .order('CreatedOn', desc=True)
        
        if search:
            query = query.or_(f"L1_Prompt.ilike.%{search}%,PromptID.ilike.%{search}%")
        
        if client_filter:
            query = query.eq('ClientId', client_filter)
        
        prompts = query.execute()
        
        # Get unique clients for filter dropdown
        clients = supabase.table('L1PromptDetails')\
            .select('ClientId')\
            .neq('ClientId', None)\
            .execute()
        
        unique_clients = sorted(set([c['ClientId'] for c in clients.data if c['ClientId']]))
        
        return render_template('l1_prompts.html', 
                             prompts=prompts.data if prompts.data else [],
                             search=search,
                             clients=unique_clients,
                             selected_client=client_filter)
    except Exception as e:
        flash(f'Error loading L1 prompts: {str(e)}', 'error')
        return render_template('l1_prompts.html', prompts=[], clients=[])

@app.route('/l2-prompts')
def l2_prompts():
    """View all L2 prompts"""
    try:
        search = request.args.get('search', '')
        l1_filter = request.args.get('l1_prompt', '')
        client_filter = request.args.get('client', '')
        
        query = supabase.table('L2PromptDetails')\
            .select('*, L1PromptDetails(L1_Prompt, PromptID)')\
            .order('CreatedOn', desc=True)
        
        if search:
            query = query.or_(f"L2_Prompt.ilike.%{search}%,Heading.ilike.%{search}%,Subheading.ilike.%{search}%")
        
        if l1_filter:
            query = query.eq('L1_PromptID', l1_filter)
        
        if client_filter:
            query = query.eq('ClientId', client_filter)
        
        prompts = query.execute()
        
        # Get unique L1 prompts for filter dropdown
        l1_prompts = supabase.table('L1PromptDetails')\
            .select('PromptID, L1_Prompt')\
            .execute()
        
        # Get unique clients for filter dropdown
        clients = supabase.table('L2PromptDetails')\
            .select('ClientId')\
            .neq('ClientId', None)\
            .execute()
        
        unique_clients = sorted(set([c['ClientId'] for c in clients.data if c['ClientId']]))
        
        return render_template('l2_prompts.html', 
                             prompts=prompts.data if prompts.data else [],
                             l1_prompts=l1_prompts.data if l1_prompts.data else [],
                             clients=unique_clients,
                             search=search,
                             selected_l1=l1_filter,
                             selected_client=client_filter)
    except Exception as e:
        flash(f'Error loading L2 prompts: {str(e)}', 'error')
        return render_template('l2_prompts.html', prompts=[], l1_prompts=[], clients=[])

@app.route('/l1/edit/<prompt_id>', methods=['GET', 'POST'])
def edit_l1(prompt_id):
    """Edit L1 prompt"""
    if request.method == 'POST':
        try:
            data = {
                'L1_Prompt': request.form['l1_prompt'],
                'ClientId': request.form['client_id'] or None,
                'IsActive': request.form.get('is_active', 'Y'),
                'LastModifiedDate': datetime.now().isoformat()
            }
            
            response = supabase.table('L1PromptDetails')\
                .update(data)\
                .eq('PromptID', prompt_id)\
                .execute()
            
            flash('L1 prompt updated successfully!', 'success')
            return redirect(url_for('l1_prompts'))
            
        except Exception as e:
            flash(f'Error updating prompt: {str(e)}', 'error')
    
    try:
        # Get the prompt to edit
        response = supabase.table('L1PromptDetails')\
            .select('*')\
            .eq('PromptID', prompt_id)\
            .single()\
            .execute()
        
        prompt = response.data
        return render_template('edit_l1.html', prompt=prompt)
    except Exception as e:
        flash(f'Error loading prompt: {str(e)}', 'error')
        return redirect(url_for('l1_prompts'))

@app.route('/l2/edit/<int:prompt_id>', methods=['GET', 'POST'])
def edit_l2(prompt_id):
    """Edit L2 prompt"""
    if request.method == 'POST':
        try:
            data = {
                'L2_Prompt': request.form['l2_prompt'],
                'L1_PromptID': request.form['l1_prompt_id'] or None,
                'ClientId': request.form['client_id'] or None,
                'CategoryUID': request.form['category_uid'] or None,
                'Heading': request.form['heading'] or None,
                'Subheading': request.form['subheading'] or None,
                'Model': request.form['model'] or None,
                'Priority': int(request.form['priority']) if request.form['priority'] else None,
                'Orders': request.form['orders'] or None,
                'Render': request.form.get('render', 'Y'),
                'IsActive': request.form.get('is_active', 'Y'),
                'LastModifiedDate': datetime.now().isoformat()
            }
            
            response = supabase.table('L2PromptDetails')\
                .update(data)\
                .eq('id', prompt_id)\
                .execute()
            
            flash('L2 prompt updated successfully!', 'success')
            return redirect(url_for('l2_prompts'))
            
        except Exception as e:
            flash(f'Error updating prompt: {str(e)}', 'error')
    
    try:
        # Get the prompt to edit
        response = supabase.table('L2PromptDetails')\
            .select('*, L1PromptDetails(L1_Prompt, PromptID)')\
            .eq('id', prompt_id)\
            .single()\
            .execute()
        
        prompt = response.data
        
        # Get all L1 prompts for dropdown
        l1_prompts = supabase.table('L1PromptDetails')\
            .select('PromptID, L1_Prompt')\
            .execute()
        
        return render_template('edit_l2.html', 
                             prompt=prompt, 
                             l1_prompts=l1_prompts.data if l1_prompts.data else [])
    except Exception as e:
        flash(f'Error loading prompt: {str(e)}', 'error')
        return redirect(url_for('l2_prompts'))

@app.route('/l1/add', methods=['GET', 'POST'])
def add_l1():
    """Add new L1 prompt"""
    if request.method == 'POST':
        try:
            data = {
                'PromptID': request.form['prompt_id'],
                'L1_Prompt': request.form['l1_prompt'],
                'ClientId': request.form['client_id'] or None,
                'IsActive': request.form.get('is_active', 'Y'),
                'CreatedOn': datetime.now().isoformat(),
                'LastModifiedDate': datetime.now().isoformat()
            }
            
            response = supabase.table('L1PromptDetails')\
                .insert(data)\
                .execute()
            
            flash('L1 prompt added successfully!', 'success')
            return redirect(url_for('l1_prompts'))
            
        except Exception as e:
            flash(f'Error adding prompt: {str(e)}', 'error')
    
    return render_template('add_prompt.html', prompt_type='l1')

@app.route('/l2/add', methods=['GET', 'POST'])
def add_l2():
    """Add new L2 prompt"""
    if request.method == 'POST':
        try:
            data = {
                'PromptID': request.form['prompt_id'],
                'L2_Prompt': request.form['l2_prompt'],
                'L1_PromptID': request.form['l1_prompt_id'] or None,
                'ClientId': request.form['client_id'] or None,
                'CategoryUID': request.form['category_uid'] or None,
                'Heading': request.form['heading'] or None,
                'Subheading': request.form['subheading'] or None,
                'Model': request.form['model'] or None,
                'Priority': int(request.form['priority']) if request.form['priority'] else None,
                'Orders': request.form['orders'] or None,
                'Render': request.form.get('render', 'Y'),
                'IsActive': request.form.get('is_active', 'Y'),
                'CreatedOn': datetime.now().isoformat(),
                'LastModifiedDate': datetime.now().isoformat()
            }
            
            response = supabase.table('L2PromptDetails')\
                .insert(data)\
                .execute()
            
            flash('L2 prompt added successfully!', 'success')
            return redirect(url_for('l2_prompts'))
            
        except Exception as e:
            flash(f'Error adding prompt: {str(e)}', 'error')
    
    # Get all L1 prompts for dropdown
    try:
        l1_prompts = supabase.table('L1PromptDetails')\
            .select('PromptID, L1_Prompt')\
            .execute()
    except:
        l1_prompts = {'data': []}
    
    return render_template('add_prompt.html', 
                         prompt_type='l2', 
                         l1_prompts=l1_prompts.data if l1_prompts.data else [])

@app.route('/l1/delete/<prompt_id>')
def delete_l1(prompt_id):
    """Delete L1 prompt"""
    try:
        # First check if there are any L2 prompts associated
        l2_prompts = supabase.table('L2PromptDetails')\
            .select('id')\
            .eq('L1_PromptID', prompt_id)\
            .execute()
        
        if l2_prompts.data:
            flash('Cannot delete L1 prompt: There are L2 prompts associated with it', 'error')
            return redirect(url_for('l1_prompts'))
        
        response = supabase.table('L1PromptDetails')\
            .delete()\
            .eq('PromptID', prompt_id)\
            .execute()
        
        flash('L1 prompt deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting prompt: {str(e)}', 'error')
    
    return redirect(url_for('l1_prompts'))

@app.route('/l2/delete/<int:prompt_id>')
def delete_l2(prompt_id):
    """Delete L2 prompt"""
    try:
        response = supabase.table('L2PromptDetails')\
            .delete()\
            .eq('id', prompt_id)\
            .execute()
        
        flash('L2 prompt deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting prompt: {str(e)}', 'error')
    
    return redirect(url_for('l2_prompts'))

@app.route('/api/l1/<prompt_id>')
def get_l1_details(prompt_id):
    """API endpoint to get L1 prompt details"""
    try:
        response = supabase.table('L1PromptDetails')\
            .select('*')\
            .eq('PromptID', prompt_id)\
            .single()\
            .execute()
        
        return jsonify(response.data)
    except:
        return jsonify({'error': 'Prompt not found'}), 404

@app.route('/api/l2/count-by-l1')
def count_l2_by_l1():
    """API endpoint to count L2 prompts by L1"""
    try:
        response = supabase.table('L2PromptDetails')\
            .select('L1_PromptID, id', count='exact')\
            .group('L1_PromptID')\
            .execute()
        
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)