odoo.define('real_estate_mod_cons.widget', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');
    var core = require('web.core');

    var Many2ManyCheckBoxesMultiCol = AbstractField.extend({
        template: 'Many2ManyCheckBoxesMultiCol',
        events: _.extend({}, AbstractField.prototype.events, {
            change: '_onChange',
        }),
        specialData: "_fetchSpecialRelation",
        supportedFieldTypes: ['many2many'],
        init: function () {
            this._super.apply(this, arguments);
            this.m2mValues = this.record.specialData[this.name];
        },

        isSet: function () {
            return true;
        },

        _render: function () {
            var self = this;
            this._super.apply(this, arguments);
            _.each(this.value.res_ids, function (id) {
                self.$('input[data-record-id="' + id + '"]').prop('checked', true);
            });
        },

        _renderReadonly: function () {
            this.$("input").prop("disabled", true);
        },
        
        _onChange: function () {
            var ids = _.map(this.$('input:checked'), function (input) {
                return $(input).data("record-id");
            });
            this._setValue({
                operation: 'REPLACE_WITH',
                ids: ids,
            });
        },
    });

    registry.add('many2many_checkboxesSixc', Many2ManyCheckBoxesMultiCol);

});