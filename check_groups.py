from app import app, Group, db

with app.app_context():
    groups = Group.query.all()
    print(f'Groups found: {len(groups)}')
    for g in groups[:10]:
        print(f'- {g.name}: {g.description}')
    
    # Check if groups 101-108 exist
    required_groups = ['101', '102', '103', '104', '105', '106', '107', '108']
    existing_groups = [g.name for g in groups]
    
    print(f'\nRequired groups: {required_groups}')
    print(f'Existing groups: {existing_groups}')
    
    missing_groups = [g for g in required_groups if g not in existing_groups]
    print(f'Missing groups: {missing_groups}')
    
    if missing_groups:
        print(f'\nCreating missing groups...')
        for group_name in missing_groups:
            new_group = Group(name=group_name, description=f'{group_name}-guruh')
            db.session.add(new_group)
        db.session.commit()
        print('Missing groups created successfully!')
        
        # Check again
        groups = Group.query.all()
        print(f'\nTotal groups after creation: {len(groups)}')
        for g in groups:
            print(f'- {g.name}: {g.description}')
