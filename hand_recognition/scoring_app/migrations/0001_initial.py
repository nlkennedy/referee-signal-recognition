# Generated by Django 2.2.8 on 2021-02-19 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('team_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='TeamMatches',
            fields=[
                ('team_match_id', models.AutoField(primary_key=True, serialize=False)),
                ('date_played', models.DateField(auto_now=True)),
                ('done', models.BooleanField(default=False)),
                ('away_team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_team', to='scoring_app.Teams')),
                ('home_team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_team', to='scoring_app.Teams')),
            ],
        ),
        migrations.CreateModel(
            name='Players',
            fields=[
                ('player_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('team_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scoring_app.Teams')),
            ],
        ),
        migrations.CreateModel(
            name='Matches',
            fields=[
                ('match_id', models.AutoField(primary_key=True, serialize=False)),
                ('home_player_score', models.IntegerField(default=0)),
                ('away_player_score', models.IntegerField(default=0)),
                ('match_rank', models.IntegerField()),
                ('court_number', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
                ('away_player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_player', to='scoring_app.Players')),
                ('home_player_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_player', to='scoring_app.Players')),
                ('team_match_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scoring_app.TeamMatches')),
            ],
        ),
        migrations.CreateModel(
            name='Games',
            fields=[
                ('game_id', models.AutoField(primary_key=True, serialize=False)),
                ('home_player_score', models.IntegerField(default=0)),
                ('away_player_score', models.IntegerField(default=0)),
                ('game_number', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
                ('match_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scoring_app.Matches')),
            ],
        ),
    ]
