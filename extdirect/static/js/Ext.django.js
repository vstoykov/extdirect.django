//
// define some helpers for django / ExtDirect
//
 
Ext.ns('Ext.django');


Ext.django.booleanFieldRenderer = function (obj) {
    return obj && 1 || 0;
}
    
Ext.django.FKRenderer = function(obj) {
    if (obj && obj.__unicode__) return obj.__unicode__;
    return obj;
}

Ext.django.M2MRenderer = function(obj) {
    if (obj) {
        if (Ext.isArray(obj) && obj.length > 0) {
            return obj.map(Ext.django.FKRenderer).join(', ');
        }
        if (Ext.isObject(obj)) return Ext.django.FKRenderer(obj);
        
    }
    return obj;
}

    
    

Ext.django.Store = Ext.extend(Ext.data.DirectStore, {
    // a direct store for django models 
    constructor:function(config) {
        var baseParams = Ext.applyIf(config.baseParams, {
            start:0
            ,limit:50
            ,meta:true
        });
        
        var config = Ext.applyIf(config, {
            remoteSort:true
            ,fields:config.fields || []
            ,root:'records'
            ,baseParams:baseParams
            ,autoLoad:true
            });

        Ext.django.Store.superclass.constructor.call( this, config );
     }
});

 
Ext.django.IndexStore = Ext.extend(Ext.django.Store, {
    // a direct store for reading django models id/name pairs (combos for FK/M2M)
    constructor:function(config) {
        // dummy
        Ext.django.IndexStore.superclass.constructor.call( this, config );
     }
});
 
   
Ext.django.Combo = Ext.extend(Ext.ux.AwesomeCombo, {
    // direct model AwesomeCombo
    constructor:function(config) {
        var baseParams = {}       
        var model = config.model.replace('.', '_');
        var config = Ext.applyIf(config, {
            valueField:'id'
            ,displayField:'__unicode__'
            ,triggerAction:'all'
            ,format:'object'
            ,store: new Ext.django.IndexStore({api:{read:django[model].read}})
            ,emptyText:'choose :'
            ,typeAhead:false
            ,mode:'local'
            ,editable:false              
        });
        Ext.django.Combo.superclass.constructor.call( this, config );
    }
});

Ext.reg('djangocombo', Ext.django.Combo);
 
   
Ext.django.Grid = Ext.extend(Ext.grid.EditorGridPanel, {

	limit:10
	,loadMask:true
    ,columnsConfig:[]
    ,model:'app.ModelName'
    ,editable:false
    ,initComponent: function() {
        
        model = this.model.replace('.','_')
        this.columns = [];
    	this.viewConfig = Ext.apply(this.viewConfig || {forceFit:true}, {onDataChange:this.onDataChange});

        this.selModel = new Ext.grid.RowSelectionModel({
            moveEditorOnEnter:false
            ,singleSelect:false
        });
        
        this.bbar = new Ext.PagingToolbar({
            displayInfo:true
            ,hidden:true
            ,pageSize:this.limit
            ,prependButtons:true
            
        });
       
        var storeConfig = {
            autoSave:true
            ,api:{
                read:django[model].read
            }
            ,baseParams:{
                meta:true
               ,fields:this.fields || []
               ,colModel:true
              }
        }
        
        if (this.editable) {
            this.editor = new Ext.ux.grid.RowEditor({
                saveText: 'Update'
            });
            storeConfig['api'] = django[model]
            this.plugins = [this.editor]
            storeConfig['writer'] = new Ext.data.JsonWriter({
                 encode:false
                ,encodeDelete:true
                ,writeAllFields:true
          	})
            
            this.tbar =  [{
                    text: 'Add',
                    iconCls: 'icon-add',
                    handler: this.onAdd,
                    scope:this
                }, '-', {
                    text: 'Delete',
                    iconCls: 'icon-delete',
                    handler: this.onDelete,
                    scope:this
                }, '-']
                 
                 
        }   
        this.store = new Ext.django.Store( storeConfig );
        this.store.on('load', function(store, records) {
            // auto show paging toolbat
            if (store.getTotalCount() > this.limit) this.getBottomToolbar().show();
        }, this);
        /*
        Ext.data.DirectStore({
    		fields:[]
    		,autoSave:true
    		,remoteSort: true
    		,baseParams:{schema:"accelrh", table:"client"}
          	,sortInfo:{field:"", direction:""}
          	,writer:new Ext.data.JsonWriter({
                encode:false
                ,encodeDelete:true
          	})
          	,paramsAsHash:false
            ,paramOrder:this.paramOrder
          	,api:this.api
        });
        */
       
        Ext.django.Grid.superclass.initComponent.apply( this, arguments );
        this.on('beforeedit', function() {
            if (!this.editable) return false;
        }, this);
        this.getBottomToolbar().bindStore(this.store);
    }

    ,onDataChange:function() {
        var columns = this.ds.reader.jsonData.columns;
        var columns2 = columns;
        // override with custom colModel if any
        if (this.grid.columnsConfig && this.grid.columnsConfig.length > 0) {
            Ext.each(this.grid.columnsConfig, function(item) {
                var added = false;
                Ext.each(columns, function(item2) {
                    if (item.name && item2.name && (item2.name == item.name) ) {
                        colConfig = item2;
                        Ext.apply(colConfig, item);                       
                        added = true;
                    }
                });
                if (!added) {
                    columns2.push( item );
                }
            });
        }
        this.cm.setConfig(columns2);
        this.syncFocusEl(0);
    }

   
    // override to make a correct comparaison of complex object
    ,onEditComplete : function(ed, value, startValue){
        this.editing = false;
        this.lastActiveEditor = this.activeEditor;
        this.activeEditor = null;

        var r = ed.record,
            field = this.colModel.getDataIndex(ed.col);
        value = this.postEditValue(value, startValue, r, field);
        if(this.forceValidation === true || Ext.encode(value) !== Ext.encode(startValue)){
            var e = {
                grid: this,
                record: r,
                field: field,
                originalValue: startValue,
                value: value,
                row: ed.row,
                column: ed.col,
                cancel:false
            };
            if(this.fireEvent("validateedit", e) !== false && !e.cancel && Ext.encode(value) !== Ext.encode(startValue)){
                r.set(field, e.value);
                delete e.cancel;
                this.fireEvent("afteredit", e);
            }
            else {
                //console.log('IS NOT VALID');
            }
        }
        this.view.focusCell(ed.row, ed.col);
    }
    ,onAdd:function(btn, ev) {
        var store = this.getStore();
         var u = new store.recordType({});
        this.editor.stopEditing();
        store.insert(0, u);
        this.editor.startEditing(0);
    }
    ,onDelete:function() {
        var rec = this.getSelectionModel();
        rec = rec.getSelected();
        if (!rec) {
            return false;
        }
        var store = this.getStore();
        store.remove(rec);
    }

}); 
    
    
Ext.reg('djangogrid', Ext.django.Grid);
    