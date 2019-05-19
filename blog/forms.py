from django import forms

from blog.models import Comment, BaseReaction, RecipeReaction


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

class ReactionForm(forms.Form):
    recipe_id = forms.IntegerField()
    reaction = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    def clean_reaction(self):
        reaction = self.cleaned_data['reaction']
        if reaction not in BaseReaction.ALL:
            raise forms.ValidationError('Invalid reaction')
        return reaction

    def save(self):
        reaction, created = RecipeReaction.objects.get_or_create(
            user=self.user,
            recipe_id=self.cleaned_data['recipe_id'],
            defaults={
                'status': self.cleaned_data['reaction']
            }
        )

        if not created and reaction.status == self.cleaned_data['reaction']:
            reaction.delete()
        elif not created:
            reaction.status = self.cleaned_data['reaction']
            reaction.save()